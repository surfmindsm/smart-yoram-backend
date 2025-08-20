from fastapi import APIRouter, Body, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core import security
from app.core.config import settings
from app.core.redis import redis_client

from app import models

spec_router = APIRouter()

# In-memory stores to unblock FE integration quickly.
_GPT_CONFIGS: Dict[int, Dict[str, Any]] = {}
_AGENTS: Dict[str, Dict[str, Any]] = {}
_CHAT_HISTORIES: List[Dict[str, Any]] = []
_CHAT_MESSAGES: Dict[str, List[Dict[str, Any]]] = {}
_CHURCH_DB_CONFIG: Dict[int, Dict[str, Any]] = {}


# -----------------------------
# Auth
# -----------------------------
@spec_router.post("/auth/login")
def spec_login(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    스펙 호환 로그인 엔드포인트.
    Request JSON: {"email": str, "password": str}
    Response JSON은 스펙의 success 래핑 구조로 반환.
    """
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="email and password are required")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    token = security.create_access_token(subject=user.id)
    return {
        "success": True,
        "data": {
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "church_id": user.church_id,
                "church_name": None,
            },
        },
    }


# -----------------------------
# Church: GPT Config & System Status
# -----------------------------
@spec_router.put("/church/gpt-config")
def set_gpt_config(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),  # noqa: F401 (reserved for future persistence)
    current_user: models.User = Depends(lambda: None),  # placeholder, add auth later
) -> Dict[str, Any]:
    """
    GPT API 키/모델 설정 저장 (임시 인메모리). 실제 영속화는 후속 작업에서 Alembic 모델로 처리.
    """
    # NOTE: 임시로 church_id=1에 저장. 추후 JWT/컨텍스트에서 church_id 식별 필요
    church_id = 1
    _GPT_CONFIGS[church_id] = {
        "apiKey": payload.get("apiKey"),
        "model": payload.get("model", "gpt-4"),
        "maxTokens": payload.get("maxTokens", 4000),
        "temperature": payload.get("temperature", 0.7),
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }
    return {"success": True}


@spec_router.get("/church/profile")
def church_profile(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """교회 정보 조회 (스펙 형식).
    현재는 인메모리 및 환경변수 기반으로 더미 값을 반환합니다.
    """
    church_id = 1
    gpt_cfg = _GPT_CONFIGS.get(church_id)
    agents_count = len(_AGENTS)
    # 실제 DB 연결 상태 반영
    db_ok = True
    try:
        db.execute("SELECT 1").scalar()
    except Exception:
        db_ok = False
    profile = {
        "id": str(church_id),
        "name": "예시교회",
        "subscriptionPlan": "premium",
        "maxAgents": 50,
        "currentAgentsCount": agents_count,
        "gptApiConfigured": bool(gpt_cfg and gpt_cfg.get("apiKey")),
        "databaseConnected": db_ok,
        "lastSync": datetime.utcnow().isoformat() + "Z",
        "monthlyUsage": {
            "totalTokens": 0,
            "totalRequests": 0,
            "totalCost": 0.0,
            "remainingQuota": 100000,
        },
    }
    return {"success": True, "data": profile}


@spec_router.get("/church/system-status")
def system_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """스펙 형식의 시스템 상태 응답.
    기존 health 체크를 재구성하여 스펙과 유사한 필드를 제공.
    """
    # Database
    db_ok = True
    try:
        db.execute("SELECT 1").scalar()
    except Exception:
        db_ok = False

    # GPT
    church_id = 1
    gpt_cfg = _GPT_CONFIGS.get(church_id)
    gpt_status = {
        "configured": bool(gpt_cfg and gpt_cfg.get("apiKey")),
        "model": (gpt_cfg or {}).get("model", "gpt-4"),
        "lastTest": datetime.utcnow().isoformat() + "Z",
        "status": "active" if gpt_cfg and gpt_cfg.get("apiKey") else "inactive",
    }

    # Agents stats (spec summary)
    total_agents = len(_AGENTS)
    active_agents = sum(1 for a in _AGENTS.values() if a.get("isActive", True))
    inactive_agents = total_agents - active_agents

    data = {
        "gptApi": gpt_status,
        "database": {
            "connected": db_ok,
            "lastSync": datetime.utcnow().isoformat() + "Z",
            "tablesCount": 0,
            "status": "healthy" if db_ok else "unavailable",
        },
        "agents": {
            "total": total_agents,
            "active": active_agents,
            "totalTokensThisMonth": 0,
            "totalCostThisMonth": 0.0,
        },
    }

    return {"success": True, "data": data}


# -----------------------------
# Agents
# -----------------------------
@spec_router.get("/agents")
def list_agents() -> Dict[str, Any]:
    agents_list: List[Dict[str, Any]] = []
    for a in _AGENTS.values():
        # 스펙 호환 필드 매핑
        agents_list.append(
            {
                "id": a.get("id"),
                "name": a.get("name"),
                "category": a.get("category"),
                "description": a.get("description"),
                "detailedDescription": a.get("detailedDescription"),
                "icon": a.get("icon", "🤖"),
                "usage": a.get("usage", 0),
                "isActive": a.get("isActive", True),
                "templates": a.get("templates", []),
                "createdAt": a.get("createdAt"),
                "updatedAt": a.get("updatedAt"),
                "totalTokensUsed": a.get("totalTokensUsed", 0),
                "totalCost": a.get("totalCost", 0.0),
                "systemPrompt": a.get("systemPrompt", ""),
                "templateId": a.get("templateId"),
                "version": a.get("version", "1.0.0"),
            }
        )
    stats = {
        "total_agents": len(agents_list),
        "active_agents": sum(1 for a in agents_list if a.get("isActive", True)),
        "inactive_agents": sum(1 for a in agents_list if not a.get("isActive", True)),
        "total_usage": sum(int(a.get("usage", 0)) for a in agents_list),
    }
    return {"success": True, "data": {"agents": agents_list, "stats": stats}}


@spec_router.post("/agents")
def create_agent(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    agent_id = str(uuid4())
    agent = {
        "id": agent_id,
        "name": payload.get("name"),
        "category": payload.get("category"),
        "description": payload.get("description"),
        "detailedDescription": payload.get("detailedDescription"),
        "icon": payload.get("icon", "🤖"),
        "systemPrompt": payload.get("systemPrompt", ""),
        "isActive": payload.get("isActive", True),
        "usage": 0,
        "templateId": payload.get("templateId"),
        "totalTokensUsed": 0,
        "totalCost": 0.0,
        "version": payload.get("version", "1.0.0"),
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }
    _AGENTS[agent_id] = agent
    return {"success": True, "data": agent}


@spec_router.get("/agents/{agent_id}")
def get_agent(agent_id: str) -> Dict[str, Any]:
    agent = _AGENTS.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"success": True, "data": agent}


@spec_router.put("/agents/{agent_id}")
def update_agent(agent_id: str, payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    agent = _AGENTS.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.update({k: v for k, v in payload.items() if v is not None})
    agent["updatedAt"] = datetime.utcnow().isoformat() + "Z"
    return {"success": True, "data": agent}


@spec_router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str) -> Dict[str, Any]:
    if agent_id in _AGENTS:
        del _AGENTS[agent_id]
        return {"success": True}
    raise HTTPException(status_code=404, detail="Agent not found")


@spec_router.get("/agents/templates/official")
def official_templates() -> Dict[str, Any]:
    return {
        "success": True,
        "data": [
            {
                "id": "official-template-1",
                "name": "설교 준비 도우미",
                "category": "설교 지원",
                "description": "성경 해석, 설교문 작성, 적용점 개발을 도와주는 전문 AI",
                "detailedDescription": "설교 준비의 전 과정을 체계적으로 지원하는 전문 AI 에이전트입니다...",
                "icon": "📖",
                "systemPrompt": "당신은 설교 준비를 전문적으로 도와주는 AI입니다...",
                "isOfficial": True,
                "version": "2.1.0",
                "createdBy": "Smart Yoram Team",
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
            {
                "id": "official-template-2",
                "name": "목양 및 심방 도우미",
                "category": "목양 관리",
                "description": "성도 상담, 심방 계획, 목양 지도를 도와주는 전문 AI",
                "detailedDescription": "목양과 심방의 모든 단계를 전문적으로 지원하는 AI 에이전트입니다...",
                "icon": "❤️",
                "systemPrompt": "당신은 목양과 심방을 전문적으로 도와주는 AI입니다...",
                "isOfficial": True,
                "version": "1.8.0",
                "createdBy": "Smart Yoram Team",
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
        ],
    }


# -----------------------------
# Chat
# -----------------------------
@spec_router.get("/chat/histories")
def list_chat_histories(
    include_messages: Optional[bool] = Query(False),
) -> Dict[str, Any]:
    data = []
    for h in _CHAT_HISTORIES:
        item = {**h}
        if include_messages:
            msgs = _CHAT_MESSAGES.get(h["id"], [])
            item["messages"] = msgs[-2:] if len(msgs) > 2 else msgs
        data.append(item)
    return {"success": True, "data": data}


@spec_router.post("/chat/messages")
def post_chat_message(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    chat_history_id = payload.get("chat_history_id") or str(uuid4())
    agent_id = payload.get("agent_id")
    content = payload.get("content", "")

    # 새 히스토리 자동 생성 (없을 경우)
    if not any(h["id"] == chat_history_id for h in _CHAT_HISTORIES):
        _CHAT_HISTORIES.append(
            {
                "id": chat_history_id,
                "title": content or "새 대화",
                "agentName": "설교 도우미",
                "isBookmarked": False,
                "messageCount": 0,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        )

    # 메시지 구성
    user_msg = {
        "id": str(uuid4()),
        "content": content,
        "role": "user",
        "tokensUsed": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    ai_msg = {
        "id": str(uuid4()),
        "content": f"요청하신 내용에 대한 임시 응답입니다: {content}",
        "role": "assistant",
        "tokensUsed": 150,
        "dataSources": [],
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    # 저장
    _CHAT_MESSAGES.setdefault(chat_history_id, []).extend([user_msg, ai_msg])
    # messageCount 갱신
    for h in _CHAT_HISTORIES:
        if h["id"] == chat_history_id:
            h["messageCount"] = len(_CHAT_MESSAGES.get(chat_history_id, []))
            h["timestamp"] = datetime.utcnow().isoformat() + "Z"
            break

    return {"success": True, "data": {"user_message": user_msg, "ai_response": ai_msg}}


@spec_router.post("/chat/histories")
def create_chat_history(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """새 채팅 시작 (스펙)."""
    history_id = str(uuid4())
    title = payload.get("title", "새 대화")
    agent_id = payload.get("agent_id")
    history = {
        "id": history_id,
        "title": title,
        "agentName": (
            _AGENTS.get(agent_id, {}).get("name", "설교 도우미")
            if agent_id
            else "설교 도우미"
        ),
        "isBookmarked": False,
        "messageCount": 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    _CHAT_HISTORIES.append(history)
    _CHAT_MESSAGES.setdefault(history_id, [])
    return {"success": True, "data": history}


@spec_router.get("/chat/histories/{history_id}/messages")
def get_chat_history_messages(history_id: str) -> Dict[str, Any]:
    msgs = _CHAT_MESSAGES.get(history_id)
    if msgs is None:
        raise HTTPException(status_code=404, detail="Chat history not found")
    return {"success": True, "data": msgs}


@spec_router.put("/chat/histories/{history_id}")
def update_chat_history(
    history_id: str, payload: Dict[str, Any] = Body(...)
) -> Dict[str, Any]:
    for h in _CHAT_HISTORIES:
        if h["id"] == history_id:
            if "title" in payload and payload["title"] is not None:
                h["title"] = payload["title"]
            if "isBookmarked" in payload and payload["isBookmarked"] is not None:
                h["isBookmarked"] = bool(payload["isBookmarked"])
            h["timestamp"] = datetime.utcnow().isoformat() + "Z"
            return {"success": True, "data": h}
    raise HTTPException(status_code=404, detail="Chat history not found")


@spec_router.delete("/chat/histories/{history_id}")
def delete_chat_history(history_id: str) -> Dict[str, Any]:
    found = False
    for idx, h in enumerate(_CHAT_HISTORIES):
        if h["id"] == history_id:
            _CHAT_HISTORIES.pop(idx)
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="Chat history not found")
    _CHAT_MESSAGES.pop(history_id, None)
    return {"success": True}


@spec_router.get("/chat/system-db-status")
def chat_system_db_status() -> Dict[str, Any]:
    tables = ["members", "attendance", "donations", "events"]
    return {
        "success": True,
        "data": {
            "connected": True,
            "tables_found": tables,
            "last_sync": datetime.utcnow().isoformat() + "Z",
        },
    }


# -----------------------------
# Church DB Query (internal)
# -----------------------------
@spec_router.post("/church/database/query")
def church_database_query(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    # Return a deterministic mock result matching the spec structure
    if payload.get("query_type") == "members_absent":
        result = [
            {
                "member_id": "12345",
                "name": "김철수",
                "weeks_absent": 3,
                "last_attendance": "2025-07-20",
            }
        ]
    else:
        result = []
    summary = "4주 연속 결석자 {}명 발견".format(len(result)) if result else "결과 없음"
    return {"success": True, "data": {"query_result": result, "summary": summary}}


# -----------------------------
# Analytics
# -----------------------------
@spec_router.get("/analytics/usage")
def analytics_usage() -> Dict[str, Any]:
    """GPT API 사용량 통계 (스펙 형식)."""
    today = datetime.utcnow().date().isoformat()
    data = {
        "current_month": {
            "total_tokens": 0,
            "total_requests": 0,
            "cost_usd": 0.0,
        },
        "daily_usage": [
            {
                "date": today,
                "tokens": 0,
                "requests": 0,
                "cost": 0.0,
            }
        ],
        "agent_usage": [
            {
                "agent_id": a.get("id"),
                "agent_name": a.get("name"),
                "tokens": a.get("totalTokensUsed", 0),
                "requests": a.get("usage", 0),
            }
            for a in _AGENTS.values()
        ],
    }
    return {"success": True, "data": data}


@spec_router.post("/church/database/config")
def set_church_db_config(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """교회 데이터베이스 연결 설정 저장 (인메모리)."""
    church_id = 1
    _CHURCH_DB_CONFIG[church_id] = {
        "db_type": payload.get("db_type", "postgresql"),
        "host": payload.get("host"),
        "port": payload.get("port"),
        "database_name": payload.get("database_name"),
        "username": payload.get("username"),
        "password": payload.get("password"),
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }
    return {"success": True}


@spec_router.get("/church/database/test-connection")
def test_church_db_connection(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """데이터베이스 연결 테스트 (현행 세션 기준)."""
    connected = True
    try:
        db.execute("SELECT 1").scalar()
    except Exception:
        connected = False
    tables_found = ["members", "attendance", "donations", "events"] if connected else []
    return {
        "success": True,
        "data": {
            "connected": connected,
            "tables_found": tables_found,
            "last_sync": datetime.utcnow().isoformat() + "Z",
        },
    }
