from typing import Any, List
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
                agent_name = getattr(agent, 'name', 'Unknown') if agent else "Unknown"
            except:
                pass

            history_dict = {
                "id": getattr(history, 'id', 0),
                "title": getattr(history, 'title', ''),
                "agent_name": agent_name,
                "is_bookmarked": getattr(history, 'is_bookmarked', False),
                "message_count": getattr(history, 'message_count', 0),
                "timestamp": getattr(history, 'updated_at', None) or getattr(history, 'created_at', None),
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
                            "id": getattr(msg, 'id', 0),
                            "content": getattr(msg, 'content', ''),
                            "role": getattr(msg, 'role', ''),
                            "tokens_used": getattr(msg, 'tokens_used', 0),
                            "timestamp": getattr(msg, 'created_at', None),
                        }
                        for msg in reversed(messages)
                    ]
                except Exception as e:
                    logger.warning(f"Failed to load messages for history {history.id}: {e}")
                    history_dict["messages"] = []

            histories_data.append(history_dict)
        except Exception as e:
            logger.warning(f"Failed to process history {getattr(history, 'id', 'unknown')}: {e}")
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
        # 비서 에이전트인 경우 Smart Assistant 로직 사용 (임시 주석 처리)
        # if agent.category == "secretary" and agent.enable_church_data:
        #     logger.info(f"Processing secretary agent message for agent {agent.id}")
        #     
        #     secretary_result = await secretary_agent_service.process_secretary_message(
        #         agent=agent,
        #         user_message=chat_request.content,
        #         user_id=current_user.id,
        #         db=db,
        #         chat_history_id=chat_history_id
        #     )
        #     
        #     # 비서 응답 저장
        #     assistant_message = ChatMessage(
        #         chat_history_id=chat_history_id,
        #         content=secretary_result["response"],
        #         role="assistant",
        #         tokens_used=secretary_result.get("tokens_used", 0),
        #     )
        #     db.add(assistant_message)
        #     
        #     # 통계 업데이트
        #     agent.usage_count += 1
        #     agent.total_tokens_used += secretary_result.get("tokens_used", 0)
        #     history.message_count += 2  # user + assistant
        #     
        #     db.commit()
        #     db.refresh(assistant_message)
        #     
        #     return {
        #         "success": True,
        #         "message": secretary_result["response"],
        #         "tokens_used": secretary_result.get("tokens_used", 0),
        #         "model": secretary_result.get("model", "gpt-4o-mini"),
        #         "query_type": secretary_result.get("query_type", "secretary_assistance"),
        #         "data_sources": secretary_result.get("data_sources", []),
        #         "is_secretary_agent": True,
        #         "message_id": assistant_message.id,
        #     }
        
        # 기존 일반 에이전트 로직
        church_context = {}
        if agent.church_data_sources:
            logger.info(f"🔍 Fetching church context for church_id={current_user.church_id}, sources={agent.church_data_sources}")
            church_context = get_church_context_data(
                db=db,
                church_id=current_user.church_id,
                church_data_sources=agent.church_data_sources,
                user_query=chat_request.content,
            )
            logger.info(f"📊 Church context retrieved: {list(church_context.keys()) if church_context else 'No data'}")

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
                logger.info(f"Added church context to system prompt: {len(context_text)} characters")

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
        logger.info(f"📝 응답 내용: '{response.get('content', '')[:100]}...' (길이: {len(response.get('content', ''))})")

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
                    "data_sources": (
                        list(church_context.keys()) if church_context else []
                    ),
                    # Remove detailed church_data_context from user-facing response
                    # Only include summary data for debugging if needed
                    "church_data_context": None,
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
