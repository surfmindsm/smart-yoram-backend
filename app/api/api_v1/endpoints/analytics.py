from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta, date

from app import models
from app.api import deps
from app.models.ai_agent import AIAgent, ChatMessage, ChatHistory
from app.models.church import Church
from app.services.openai_service import openai_service

router = APIRouter()


@router.get("/usage", response_model=dict)
def read_usage_analytics(
    *,
    db: Session = Depends(deps.get_db),
    period: str = Query("month", regex="^(day|week|month|year|current_month)$"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get GPT API usage statistics.
    """
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    # Calculate date range
    now = datetime.now()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    elif period in ["month", "current_month"]:
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # year
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get current period usage
    current_period_stats = db.query(
        func.sum(ChatMessage.tokens_used).label("total_tokens"),
        func.count(ChatMessage.id).label("total_requests")
    ).join(
        ChatHistory,
        ChatMessage.chat_history_id == ChatHistory.id
    ).filter(
        ChatHistory.church_id == church.id,
        ChatMessage.created_at >= start_date
    ).first()
    
    total_tokens = current_period_stats.total_tokens or 0
    total_requests = current_period_stats.total_requests or 0
    cost_usd = openai_service.calculate_cost(total_tokens, church.gpt_model or "gpt-4o-mini")
    
    # Get daily usage for the period
    daily_usage = []
    if period in ["month", "current_month"]:
        # Group by day for the current month
        daily_stats = db.query(
            func.date(ChatMessage.created_at).label("date"),
            func.sum(ChatMessage.tokens_used).label("tokens"),
            func.count(ChatMessage.id).label("requests")
        ).join(
            ChatHistory,
            ChatMessage.chat_history_id == ChatHistory.id
        ).filter(
            ChatHistory.church_id == church.id,
            ChatMessage.created_at >= start_date
        ).group_by(
            func.date(ChatMessage.created_at)
        ).order_by(
            func.date(ChatMessage.created_at)
        ).all()
        
        for stat in daily_stats:
            daily_cost = openai_service.calculate_cost(
                stat.tokens or 0, 
                church.gpt_model or "gpt-4o-mini"
            )
            daily_usage.append({
                "date": stat.date.isoformat(),
                "tokens": stat.tokens or 0,
                "requests": stat.requests or 0,
                "cost": round(daily_cost, 2)
            })
    
    # Get agent usage statistics
    agent_usage = []
    agent_stats = db.query(
        AIAgent.id,
        AIAgent.name,
        func.sum(ChatMessage.tokens_used).label("tokens"),
        func.count(ChatMessage.id).label("requests")
    ).join(
        ChatHistory,
        AIAgent.id == ChatHistory.agent_id
    ).join(
        ChatMessage,
        ChatHistory.id == ChatMessage.chat_history_id
    ).filter(
        AIAgent.church_id == church.id,
        ChatMessage.created_at >= start_date
    ).group_by(
        AIAgent.id,
        AIAgent.name
    ).order_by(
        func.sum(ChatMessage.tokens_used).desc()
    ).all()
    
    for agent_stat in agent_stats:
        agent_usage.append({
            "agent_id": agent_stat.id,
            "agent_name": agent_stat.name,
            "tokens": agent_stat.tokens or 0,
            "requests": agent_stat.requests or 0
        })
    
    # Return format matching frontend expectations
    if period == "current_month" or period == "month":
        return {
            "success": True,
            "data": {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_cost": round(cost_usd, 2),
                "daily_stats": daily_usage,
                "period": period,
                "agent_usage": agent_usage
            }
        }
    
    return {
        "success": True,
        "data": {
            "current_month": {
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "cost_usd": round(cost_usd, 2)
            },
            "daily_usage": daily_usage,
            "agent_usage": agent_usage
        }
    }


@router.get("/agents/stats", response_model=dict)
def read_agent_statistics(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int = Query(None),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get detailed statistics for agents.
    """
    query = db.query(AIAgent).filter(
        AIAgent.church_id == current_user.church_id
    )
    
    if agent_id:
        query = query.filter(AIAgent.id == agent_id)
    
    agents = query.all()
    
    if not agents:
        raise HTTPException(
            status_code=404,
            detail="No agents found"
        )
    
    agent_stats = []
    for agent in agents:
        # Get usage statistics for this agent
        stats = db.query(
            func.count(ChatMessage.id).label("total_messages"),
            func.sum(ChatMessage.tokens_used).label("total_tokens"),
            func.max(ChatMessage.created_at).label("last_used")
        ).join(
            ChatHistory,
            ChatMessage.chat_history_id == ChatHistory.id
        ).filter(
            ChatHistory.agent_id == agent.id
        ).first()
        
        # Get conversation count
        conversation_count = db.query(ChatHistory).filter(
            ChatHistory.agent_id == agent.id
        ).count()
        
        # Calculate average tokens per request
        avg_tokens = 0
        if stats.total_messages and stats.total_messages > 0:
            avg_tokens = (stats.total_tokens or 0) / stats.total_messages
        
        agent_stats.append({
            "agent_id": agent.id,
            "agent_name": agent.name,
            "category": agent.category,
            "is_active": agent.is_active,
            "total_conversations": conversation_count,
            "total_messages": stats.total_messages or 0,
            "total_tokens": stats.total_tokens or 0,
            "avg_tokens_per_message": round(avg_tokens, 2),
            "total_cost": round(agent.total_cost, 2),
            "last_used": stats.last_used.isoformat() if stats.last_used else None,
            "created_at": agent.created_at.isoformat()
        })
    
    return {
        "success": True,
        "data": agent_stats
    }


@router.get("/trends", response_model=dict)
def read_usage_trends(
    *,
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get usage trends over time.
    """
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    start_date = datetime.now() - timedelta(days=days)
    
    # Get daily trends
    trends = db.query(
        func.date(ChatMessage.created_at).label("date"),
        func.count(ChatMessage.id).label("messages"),
        func.sum(ChatMessage.tokens_used).label("tokens"),
        func.count(func.distinct(ChatHistory.user_id)).label("active_users"),
        func.count(func.distinct(ChatHistory.agent_id)).label("active_agents")
    ).join(
        ChatHistory,
        ChatMessage.chat_history_id == ChatHistory.id
    ).filter(
        ChatHistory.church_id == church.id,
        ChatMessage.created_at >= start_date
    ).group_by(
        func.date(ChatMessage.created_at)
    ).order_by(
        func.date(ChatMessage.created_at)
    ).all()
    
    trend_data = []
    for trend in trends:
        cost = openai_service.calculate_cost(
            trend.tokens or 0,
            church.gpt_model or "gpt-4o-mini"
        )
        
        trend_data.append({
            "date": trend.date.isoformat(),
            "messages": trend.messages or 0,
            "tokens": trend.tokens or 0,
            "cost": round(cost, 2),
            "active_users": trend.active_users or 0,
            "active_agents": trend.active_agents or 0
        })
    
    # Calculate growth rates
    if len(trend_data) >= 7:
        last_week = sum(t["tokens"] for t in trend_data[-7:])
        prev_week = sum(t["tokens"] for t in trend_data[-14:-7]) if len(trend_data) >= 14 else 0
        
        if prev_week > 0:
            weekly_growth = ((last_week - prev_week) / prev_week) * 100
        else:
            weekly_growth = 100 if last_week > 0 else 0
    else:
        weekly_growth = 0
    
    return {
        "success": True,
        "data": {
            "trends": trend_data,
            "summary": {
                "total_days": len(trend_data),
                "weekly_growth_rate": round(weekly_growth, 2),
                "avg_daily_tokens": round(sum(t["tokens"] for t in trend_data) / len(trend_data), 0) if trend_data else 0,
                "avg_daily_cost": round(sum(t["cost"] for t in trend_data) / len(trend_data), 2) if trend_data else 0
            }
        }
    }


@router.get("/top-queries", response_model=dict)
def read_top_queries(
    *,
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get most common query patterns.
    """
    start_date = datetime.now() - timedelta(days=days)
    
    # Get recent user messages
    messages = db.query(
        ChatMessage.content
    ).join(
        ChatHistory,
        ChatMessage.chat_history_id == ChatHistory.id
    ).filter(
        ChatHistory.church_id == current_user.church_id,
        ChatMessage.role == "user",
        ChatMessage.created_at >= start_date
    ).limit(1000).all()
    
    # Simple keyword extraction (in production, use more sophisticated NLP)
    keyword_counts = {}
    keywords_to_track = [
        "출석", "결석", "성도", "교인", "헌금", "십일조", 
        "예배", "모임", "행사", "일정", "연락처", "주소",
        "심방", "상담", "기도", "말씀", "성경", "설교"
    ]
    
    for message in messages:
        content = message.content.lower()
        for keyword in keywords_to_track:
            if keyword in content:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Sort by count and get top queries
    top_queries = sorted(
        keyword_counts.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:limit]
    
    return {
        "success": True,
        "data": {
            "top_queries": [
                {"keyword": keyword, "count": count}
                for keyword, count in top_queries
            ],
            "period_days": days,
            "total_messages_analyzed": len(messages)
        }
    }