from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import asyncio
import logging

from app import models, schemas
from app.api import deps
from app.models.ai_agent import AIAgent, ChatHistory, ChatMessage
from app.services.church_default_agent_service import ChurchDefaultAgentService
from app.schemas.ai_agent import (
    ChatHistoryCreate,
    ChatHistoryUpdate,
    ChatHistory as ChatHistorySchema,
    ChatHistoryWithMessages,
    ChatMessage as ChatMessageSchema,
    ChatRequest,
    ChatResponse,
)
from app.services.openai_service import openai_service
from app.services.church_data_context import (
    get_church_context_data,
    format_context_for_prompt,
)

# from app.services.secretary_agent_service import secretary_agent_service

logger = logging.getLogger(__name__)
router = APIRouter()


def create_secretary_prompt(
    church_data: str,
    user_query: str,
    church_name: str,
    agent: AIAgent,
    prioritize_church_data: bool = False,
    fallback_to_general: bool = True,
) -> str:
    """비서 모드용 GPT 프롬프트 생성"""

    base_prompt = agent.system_prompt or f"당신은 {church_name}의 AI 비서입니다."

    if church_data and church_data.strip() and prioritize_church_data:
        return f"""
{base_prompt}

=== 교회 데이터베이스 정보 ===
{church_data}

사용자 질문: "{user_query}"

**응답 지침:**
1. 🔍 교회 데이터에서 관련 정보를 찾을 수 있으면 **우선적으로** 활용하세요
2. 📚 교회 데이터에 없는 내용이면 일반적인 AI 지식으로 도움을 주세요  
3. 💬 답변 시 어떤 정보를 기반으로 했는지 자연스럽게 언급하세요

**좋은 답변 예시:**
- "교회 등록 정보를 확인해보니..."
- "일반적으로 이런 경우에는..."
- "교회 데이터와 함께 고려할 때..."
- "교회 현황을 바탕으로 제안드리면..."

**주의사항:**
- 교회 데이터가 부족해도 답변을 거부하지 마세요
- 사용자에게 도움이 되는 정보를 최대한 제공하세요
- 자연스럽고 친근한 톤으로 응답하세요
"""

    elif fallback_to_general:
        return f"""
{base_prompt}

교회 관련 업무를 우선적으로 도와드리며, 필요시 일반적인 질문에도 답변드립니다.

사용자와 자연스럽게 대화하면서, 교회 업무에 도움이 되는 정보를 제공해주세요.
"""

    else:
        return base_prompt


def analyze_secretary_response(
    gpt_response: str, church_data_provided: bool, user_query: str
) -> Dict[str, Any]:
    """GPT 응답을 분석하여 데이터 소스 및 쿼리 타입을 판단"""

    # 교회 데이터 관련 키워드
    church_data_keywords = [
        "교회 데이터",
        "등록 정보",
        "교회 기록",
        "데이터베이스",
        "확인해보니",
        "교회 현황",
        "등록된",
        "기록된",
    ]

    # 일반 지식 키워드
    general_knowledge_keywords = [
        "일반적으로",
        "보통",
        "제가 아는 바로는",
        "알려진",
        "경험상",
        "보편적으로",
        "전반적으로",
        "대체로",
    ]

    # 교회 관련 질문인지 판단
    church_related_keywords = [
        "교인",
        "성도",
        "예배",
        "헌금",
        "출석",
        "심방",
        "목사",
        "전도사",
        "기도",
        "찬양",
        "교회",
        "성경",
        "신앙",
        "예배당",
        "구역",
        "부서",
    ]

    is_church_related_query = any(
        keyword in user_query for keyword in church_related_keywords
    )

    used_church_data = church_data_provided and any(
        keyword in gpt_response for keyword in church_data_keywords
    )

    used_general_knowledge = any(
        keyword in gpt_response for keyword in general_knowledge_keywords
    )

    # 응답 분석
    if used_church_data and used_general_knowledge:
        query_type = "hybrid_response"
        data_sources = ["교회 데이터베이스", "AI 일반 지식"]
        church_data_used = True
        fallback_used = True
    elif used_church_data:
        query_type = "church_data_query"
        data_sources = ["교회 데이터베이스"]
        church_data_used = True
        fallback_used = False
    elif is_church_related_query and church_data_provided:
        # 교회 관련 질문이지만 교회 데이터를 활용하지 못한 경우
        query_type = "fallback_response"
        data_sources = ["AI 일반 지식"]
        church_data_used = False
        fallback_used = True
    else:
        query_type = "general_query"
        data_sources = ["AI 일반 지식"]
        church_data_used = False
        fallback_used = not church_data_provided

    return {
        "query_type": query_type,
        "data_sources": data_sources,
        "church_data_used": church_data_used,
        "fallback_used": fallback_used,
        "is_church_related_query": is_church_related_query,
    }


@router.get("/histories", response_model=dict)
def read_chat_histories(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_messages: bool = Query(False),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve chat histories for current user.
    """
    logger.debug(
        f"Reading chat histories for user {current_user.id}, church {current_user.church_id}"
    )
    try:
        query = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id,
                ChatHistory.church_id == current_user.church_id,
            )
            .order_by(desc(ChatHistory.updated_at))
        )

        histories = query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.warning(f"Failed to query chat histories: {e}")
        histories = []

    histories_data = []
    for history in histories:
        try:
            # Get agent name (with error handling)
            agent_name = "Unknown"
            try:
                agent = db.query(AIAgent).filter(AIAgent.id == history.agent_id).first()
                agent_name = getattr(agent, "name", "Unknown") if agent else "Unknown"
            except:
                pass

            history_dict = {
                "id": getattr(history, "id", 0),
                "title": getattr(history, "title", ""),
                "agent_name": agent_name,
                "is_bookmarked": getattr(history, "is_bookmarked", False),
                "message_count": getattr(history, "message_count", 0),
                "timestamp": getattr(history, "updated_at", None)
                or getattr(history, "created_at", None),
            }

            # Include recent messages if requested
            if include_messages:
                try:
                    messages = (
                        db.query(ChatMessage)
                        .filter(ChatMessage.chat_history_id == history.id)
                        .order_by(desc(ChatMessage.created_at))
                        .limit(5)
                        .all()
                    )

                    history_dict["messages"] = [
                        {
                            "id": getattr(msg, "id", 0),
                            "content": getattr(msg, "content", ""),
                            "role": getattr(msg, "role", ""),
                            "tokens_used": getattr(msg, "tokens_used", 0),
                            "timestamp": getattr(msg, "created_at", None),
                        }
                        for msg in reversed(messages)
                    ]
                except Exception as e:
                    logger.warning(
                        f"Failed to load messages for history {history.id}: {e}"
                    )
                    history_dict["messages"] = []

            histories_data.append(history_dict)
        except Exception as e:
            logger.warning(
                f"Failed to process history {getattr(history, 'id', 'unknown')}: {e}"
            )
            continue

    return {"success": True, "data": histories_data}


@router.post("/histories", response_model=ChatHistorySchema)
def create_chat_history(
    *,
    db: Session = Depends(deps.get_db),
    history_in: ChatHistoryCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Start new chat session.
    """
    # Convert string ID to int if needed
    try:
        agent_id = (
            int(history_in.agent_id)
            if isinstance(history_in.agent_id, str)
            else history_in.agent_id
        )
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid agent_id format")

    # Verify agent exists and belongs to church
    agent = (
        db.query(AIAgent)
        .filter(AIAgent.id == agent_id, AIAgent.church_id == current_user.church_id)
        .first()
    )

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Create chat history
    history_data = history_in.dict()
    history_data["agent_id"] = agent_id  # Use converted int ID
    history = ChatHistory(
        **history_data, church_id=current_user.church_id, user_id=current_user.id
    )

    db.add(history)
    db.commit()
    db.refresh(history)

    return history


@router.get("/histories/{history_id}/messages", response_model=dict)
def read_chat_messages(
    *,
    db: Session = Depends(deps.get_db),
    history_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get messages for specific chat history.
    """
    # Verify history belongs to user
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Chat history not found")

    # Get messages
    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_history_id == history_id)
        .order_by(ChatMessage.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )

    messages_data = [
        {
            "id": msg.id,
            "content": msg.content,
            "role": msg.role,
            "tokens_used": msg.tokens_used,
            "timestamp": msg.created_at,
        }
        for msg in messages
    ]

    return {"success": True, "data": messages_data}


@router.post("/messages", response_model=dict)
async def send_message(
    *,
    db: Session = Depends(deps.get_db),
    chat_request: ChatRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Send message and get AI response.
    Automatically creates chat history if chat_history_id is null and create_history_if_needed is True.
    """
    # Convert agent_id to int if needed
    try:
        agent_id = (
            int(chat_request.agent_id)
            if isinstance(chat_request.agent_id, str)
            else chat_request.agent_id
        )
    except (ValueError, TypeError) as e:
        logger.error(f"Invalid agent_id format: {e}")
        raise HTTPException(
            status_code=400, detail="Invalid agent_id format in request"
        )

    # Get agent first to validate it exists
    agent = (
        db.query(AIAgent)
        .filter(
            AIAgent.id == agent_id,
            AIAgent.church_id == current_user.church_id,
            AIAgent.is_active == True,
        )
        .first()
    )
    if not agent:
        # If no agent found, try to get/create default agent for this church
        agent = ChurchDefaultAgentService.get_or_create_default_agent(
            current_user.church_id, db
        )
        if agent.id != agent_id:
            raise HTTPException(
                status_code=404,
                detail=f"Agent {agent_id} not found. Use agent {agent.id} instead.",
            )

    # Check if agent is active
    if not agent.is_active:
        raise HTTPException(status_code=400, detail="Agent is not active")

    chat_history_id = chat_request.chat_history_id

    # Auto-create history if needed
    if chat_history_id is None and chat_request.create_history_if_needed:
        logger.info(f"Auto-creating chat history for agent {agent_id}")

        # Generate title from first part of message content
        title_preview = (
            chat_request.content[:50] + "..."
            if len(chat_request.content) > 50
            else chat_request.content
        )

        # Create new chat history
        new_history = ChatHistory(
            church_id=current_user.church_id,
            user_id=current_user.id,
            agent_id=agent.id,  # Use the actual agent ID
            title=title_preview,
            is_bookmarked=False,
            message_count=0,
        )

        db.add(new_history)
        db.commit()
        db.refresh(new_history)

        chat_history_id = new_history.id
        history = new_history
        logger.info(f"Created new chat history with ID: {chat_history_id}")

    elif chat_history_id is not None:
        # Convert string ID to int if needed
        try:
            chat_history_id = (
                int(chat_history_id)
                if isinstance(chat_history_id, str)
                else chat_history_id
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid chat_history_id format: {e}")
            raise HTTPException(
                status_code=400, detail="Invalid chat_history_id format"
            )

        # Verify existing chat history
        history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.id == chat_history_id,
                ChatHistory.user_id == current_user.id,
            )
            .first()
        )

        if not history:
            raise HTTPException(status_code=404, detail="Chat history not found")

    else:
        # chat_history_id is None and create_history_if_needed is False
        raise HTTPException(
            status_code=400,
            detail="chat_history_id is required when create_history_if_needed is False",
        )

    # Agent was already validated above

    # Get church for GPT settings
    church = (
        db.query(models.Church)
        .filter(models.Church.id == current_user.church_id)
        .first()
    )

    # Check if church has GPT API key configured
    if not church.gpt_api_key:
        # Use default API key from environment
        import os

        default_key = os.getenv("OPENAI_API_KEY")
        if default_key:
            church.gpt_api_key = default_key
        else:
            raise HTTPException(
                status_code=500, detail="GPT API key not configured for this church"
            )

    # Save user message
    user_message = ChatMessage(
        chat_history_id=chat_history_id,
        content=chat_request.content,
        role="user",
        tokens_used=0,
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    try:
        # 🆕 비서 모드 또는 비서 에이전트인 경우 처리
        logger.info(f"🔍 Debug - Agent ID: {agent.id}, Category: {agent.category}, Enable Church Data: {agent.enable_church_data}")
        logger.info(f"🔍 Debug - Request Secretary Mode: {chat_request.secretary_mode}, Prioritize Church Data: {getattr(chat_request, 'prioritize_church_data', 'N/A')}")
        
        is_secretary_mode = chat_request.secretary_mode or (
            agent.category == "secretary" and agent.enable_church_data
        )
        
        logger.info(f"🔍 Debug - Is Secretary Mode: {is_secretary_mode}")

        if is_secretary_mode:
            logger.info(f"Processing secretary mode message for agent {agent.id}")

            # 교회 데이터 컨텍스트 처리
            church_data_context = chat_request.church_data_context
            logger.info(f"🔍 Debug - Initial church_data_context: {church_data_context is not None}")
            logger.info(f"🔍 Debug - prioritize_church_data: {getattr(chat_request, 'prioritize_church_data', None)}")
            logger.info(f"🔍 Debug - agent.church_data_sources: {agent.church_data_sources}")
            
            should_get_church_data = (
                not church_data_context
                and chat_request.prioritize_church_data
                and agent.church_data_sources
            )
            
            if should_get_church_data:
                logger.info(f"📊 Retrieving church data for agent {agent.id}")
                # 교회 데이터 조회
                church_context = get_church_context_data(
                    db=db,
                    church_id=current_user.church_id,
                    church_data_sources=agent.church_data_sources,
                    user_query=chat_request.content,
                )
                logger.info(f"🔍 Debug - Retrieved church_context keys: {list(church_context.keys()) if church_context else 'None'}")

                # GPT용 컨텍스트 포맷팅
                from app.api.api_v1.endpoints.church_data import format_for_gpt_context

                church_data_context = format_for_gpt_context(
                    church_context, current_user.church_id, db
                )
                logger.info(
                    f"📊 Fresh church context retrieved: {len(church_data_context)} characters"
                )

            # 비서 프롬프트 생성
            church_name = church.name if church else f"Church {current_user.church_id}"
            secretary_prompt = create_secretary_prompt(
                church_data=church_data_context or "",
                user_query=chat_request.content,
                church_name=church_name,
                agent=agent,
                prioritize_church_data=chat_request.prioritize_church_data,
                fallback_to_general=chat_request.fallback_to_general,
            )

            # OpenAI 서비스 설정 (기존 로직 재사용)
            use_test_service = False
            try:
                from app.core.security import decrypt_data

                api_key = (
                    decrypt_data(church.gpt_api_key) if church.gpt_api_key else None
                )
                if not api_key or api_key == "":
                    api_key = church.gpt_api_key
            except Exception:
                api_key = church.gpt_api_key

            if (
                not api_key
                or api_key == ""
                or "test" in (church.gpt_api_key or "").lower()
            ):
                use_test_service = True
                logger.warning(
                    f"Using test OpenAI service for secretary mode in church {church.id}"
                )

            if use_test_service:
                from app.services.openai_test_service import TestOpenAIService

                church_openai_service = TestOpenAIService()
            else:
                from app.services.openai_service import OpenAIService

                church_openai_service = OpenAIService(api_key=api_key)

            # 메시지 히스토리 준비
            messages = []
            if chat_request.messages:
                messages = chat_request.messages
            else:
                # 기존 대화 히스토리 조회
                recent_messages = (
                    db.query(ChatMessage)
                    .filter(ChatMessage.chat_history_id == chat_history_id)
                    .order_by(desc(ChatMessage.created_at))
                    .limit(10)
                    .all()
                )
                for msg in reversed(recent_messages[1:]):  # 방금 추가된 메시지 제외
                    messages.append({"role": msg.role, "content": msg.content})

            messages.append({"role": "user", "content": chat_request.content})

            # GPT 응답 생성
            model = agent.gpt_model or church.gpt_model or "gpt-4o-mini"
            max_tokens = agent.max_tokens or church.max_tokens or 4000
            temperature = agent.temperature or church.temperature or 0.7

            logger.info(f"🤖 Secretary Mode GPT Call - Model: {model}")

            response = await church_openai_service.generate_response(
                messages=messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=secretary_prompt,
            )

            # 응답 분석
            response_analysis = analyze_secretary_response(
                gpt_response=response["content"],
                church_data_provided=bool(
                    church_data_context and church_data_context.strip()
                ),
                user_query=chat_request.content,
            )

            # AI 응답 저장
            ai_message = ChatMessage(
                chat_history_id=chat_history_id,
                content=response["content"],
                role="assistant",
                tokens_used=response["tokens_used"],
            )
            db.add(ai_message)

            # 통계 업데이트
            agent.usage_count = (agent.usage_count or 0) + 1
            agent.total_tokens_used = (agent.total_tokens_used or 0) + response[
                "tokens_used"
            ]
            agent.total_cost = (agent.total_cost or 0) + openai_service.calculate_cost(
                response["tokens_used"], model
            )

            church.current_month_tokens = (church.current_month_tokens or 0) + response[
                "tokens_used"
            ]
            church.current_month_cost = (
                church.current_month_cost or 0
            ) + openai_service.calculate_cost(response["tokens_used"], model)

            history.message_count += 2

            db.commit()
            db.refresh(ai_message)

            logger.info(
                f"✅ Secretary Response Analysis: {response_analysis['query_type']}"
            )

            return {
                "success": True,
                "data": {
                    "user_message": {
                        "id": user_message.id,
                        "content": user_message.content,
                        "role": user_message.role,
                        "timestamp": user_message.created_at,
                    },
                    "ai_response": {
                        "id": ai_message.id,
                        "content": ai_message.content,
                        "role": ai_message.role,
                        "tokens_used": ai_message.tokens_used,
                        "timestamp": ai_message.created_at,
                    },
                    "model": response.get("model", model),
                    "actual_model": response.get("model", model),
                    "total_tokens": response.get("tokens_used", 0),
                    "chat_history_id": chat_history_id,
                    # 🆕 비서 모드 메타데이터
                    "is_secretary_agent": True,
                    "data_sources": response_analysis["data_sources"],
                    "query_type": response_analysis["query_type"],
                    "church_data_used": response_analysis["church_data_used"],
                    "fallback_used": response_analysis["fallback_used"],
                },
            }

        # 기존 일반 에이전트 로직
        church_context = {}
        if agent.church_data_sources:
            logger.info(
                f"🔍 Fetching church context for church_id={current_user.church_id}, sources={agent.church_data_sources}"
            )
            church_context = get_church_context_data(
                db=db,
                church_id=current_user.church_id,
                church_data_sources=agent.church_data_sources,
                user_query=chat_request.content,
            )
            logger.info(
                f"📊 Church context retrieved: {list(church_context.keys()) if church_context else 'No data'}"
            )

        # Get recent conversation history
        recent_messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.chat_history_id == chat_request.chat_history_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(10)
            .all()
        )

        # Prepare messages for OpenAI
        messages = []
        for msg in reversed(recent_messages[1:]):  # Exclude the just-added message
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": chat_request.content})

        # Add church data context if available
        enhanced_system_prompt = agent.system_prompt
        if church_context:
            context_text = format_context_for_prompt(church_context)
            if context_text:
                # Add context to the system prompt, not the user message
                enhanced_system_prompt = agent.system_prompt + "\n\n" + context_text
                logger.info(
                    f"Added church context to system prompt: {len(context_text)} characters"
                )

        # Use test service if no valid API key is configured
        use_test_service = False

        # Try to decrypt API key, if it fails use as is
        try:
            from app.core.security import decrypt_data

            api_key = decrypt_data(church.gpt_api_key) if church.gpt_api_key else None
            if not api_key or api_key == "":
                api_key = church.gpt_api_key  # Use as is if decryption fails
        except Exception:
            api_key = church.gpt_api_key  # Use as is if decryption fails

        # Check if we should use test service
        if not api_key or api_key == "" or "test" in (church.gpt_api_key or "").lower():
            use_test_service = True
            logger.warning(f"Using test OpenAI service for church {church.id}")

        if use_test_service:
            from app.services.openai_test_service import TestOpenAIService

            church_openai_service = TestOpenAIService()
        else:
            from app.services.openai_service import OpenAIService

            church_openai_service = OpenAIService(api_key=api_key)

        # Generate AI response
        # Use enhanced system prompt (which includes church context if available)
        final_system_prompt = enhanced_system_prompt

        # Log OpenAI request details
        requested_model = church.gpt_model or "gpt-4o-mini"
        logger.info(f"🚀 OpenAI 호출 - 요청 모델: {requested_model}")
        logger.info(f"📝 DB 모델 설정: {church.gpt_model}")
        logger.info(f"📋 최대 토큰: {church.max_tokens or 4000}")
        logger.info(f"🌡️ 온도: {church.temperature or 0.7}")

        response = await church_openai_service.generate_response(
            messages=messages,
            model=requested_model,
            max_tokens=church.max_tokens or 4000,
            temperature=church.temperature or 0.7,
            system_prompt=final_system_prompt,
        )

        # Log OpenAI response details
        logger.info(f"✅ OpenAI 응답 - 실제 모델: {response.get('model', 'Unknown')}")
        logger.info(f"📊 사용 토큰: {response.get('tokens_used', 0)}")
        logger.info(f"🔄 완료 이유: {response.get('finish_reason', 'Unknown')}")
        logger.info(
            f"📝 응답 내용: '{response.get('content', '')[:100]}...' (길이: {len(response.get('content', ''))})"
        )

        # Save AI response
        ai_message = ChatMessage(
            chat_history_id=chat_history_id,
            content=response["content"],
            role="assistant",
            tokens_used=response["tokens_used"],
        )
        db.add(ai_message)

        # Update usage statistics for all agents
        agent.usage_count = (agent.usage_count or 0) + 1
        agent.total_tokens_used = (agent.total_tokens_used or 0) + response[
            "tokens_used"
        ]
        agent.total_cost = (agent.total_cost or 0) + openai_service.calculate_cost(
            response["tokens_used"], church.gpt_model or "gpt-4o-mini"
        )

        # Update church usage
        church.current_month_tokens = (church.current_month_tokens or 0) + response[
            "tokens_used"
        ]
        church.current_month_cost = (
            church.current_month_cost or 0
        ) + openai_service.calculate_cost(
            response["tokens_used"], church.gpt_model or "gpt-4o-mini"
        )

        # Update history
        history.message_count += 2

        db.commit()
        db.refresh(ai_message)

        # Prepare response data
        response_data = {
            "success": True,
            "data": {
                "user_message": {
                    "id": user_message.id,
                    "content": user_message.content,
                    "role": user_message.role,
                    "timestamp": user_message.created_at,
                },
                "ai_response": {
                    "id": ai_message.id,
                    "content": ai_message.content,
                    "role": ai_message.role,
                    "tokens_used": ai_message.tokens_used,
                    "timestamp": ai_message.created_at,
                },
                "model": response.get("model", church.gpt_model or "gpt-4o-mini"),
                "gpt_model": response.get("model", church.gpt_model or "gpt-4o-mini"),
                "actual_model": response.get(
                    "model", church.gpt_model or "gpt-4o-mini"
                ),
                "total_tokens": response.get("tokens_used", 0),
                "tokensUsed": response.get("tokens_used", 0),
                "prompt_tokens": 0,  # OpenAI response doesn't separate these in our current setup
                "completion_tokens": response.get("tokens_used", 0),
                "chat_history_id": chat_history_id,
                # 🆕 일반 에이전트도 동일한 메타데이터 구조 제공
                "is_secretary_agent": False,
                "data_sources": list(church_context.keys()) if church_context else [],
                "query_type": "general_query",
                "church_data_used": bool(church_context),
                "fallback_used": False,
            },
        }

        # Log final response data for debugging
        logger.info(
            f"📤 클라이언트 전송 - 모델: {response.get('model', 'Unknown')}, "
            f"토큰: {response.get('tokens_used', 0)}, "
            f"채팅 히스토리 ID: {chat_history_id}"
        )

        return response_data

    except Exception as e:
        # Delete the user message if AI response failed
        db.delete(user_message)
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))


@router.put("/histories/{history_id}", response_model=ChatHistorySchema)
def update_chat_history(
    *,
    db: Session = Depends(deps.get_db),
    history_id: int,
    history_in: ChatHistoryUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update chat history (title or bookmark).
    """
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Chat history not found")

    # Update history
    update_data = history_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(history, field, value)

    db.commit()
    db.refresh(history)

    return history


@router.delete("/histories/{history_id}")
def delete_chat_history(
    *,
    db: Session = Depends(deps.get_db),
    history_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete chat history and all messages.
    """
    history = (
        db.query(ChatHistory)
        .filter(ChatHistory.id == history_id, ChatHistory.user_id == current_user.id)
        .first()
    )

    if not history:
        raise HTTPException(status_code=404, detail="Chat history not found")

    db.delete(history)
    db.commit()

    return {"success": True, "message": "Chat history deleted successfully"}
