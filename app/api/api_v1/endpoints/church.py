from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app import models, schemas
from app.api import deps
from app.models.church import Church
from app.models.ai_agent import ChurchDatabaseConfig, AIAgent, ChatMessage
from app.schemas.ai_agent import (
    ChurchDatabaseConfigCreate, ChurchDatabaseConfigUpdate,
    ChurchDatabaseConfig as ChurchDatabaseConfigSchema,
    DatabaseTestResult, GPTConfigUpdate, ChurchProfile, SystemStatus
)
from app.services.church_data_service import church_data_service
from app.services.openai_service import openai_service
from app.core.security import encrypt_data, decrypt_data

router = APIRouter()


@router.get("/profile", response_model=dict)
def read_church_profile(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get church profile with usage statistics.
    """
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    # Get agent count
    agents_count = db.query(AIAgent).filter(
        AIAgent.church_id == church.id
    ).count()
    
    # Get database config status
    db_config = db.query(ChurchDatabaseConfig).filter(
        ChurchDatabaseConfig.church_id == church.id,
        ChurchDatabaseConfig.is_active == True
    ).first()
    
    # Calculate monthly usage
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_messages = db.query(
        func.count(ChatMessage.id).label("total_requests"),
        func.sum(ChatMessage.tokens_used).label("total_tokens")
    ).join(
        models.ChatHistory,
        ChatMessage.chat_history_id == models.ChatHistory.id
    ).filter(
        models.ChatHistory.church_id == church.id,
        ChatMessage.created_at >= start_of_month
    ).first()
    
    total_requests = monthly_messages.total_requests or 0
    total_tokens = monthly_messages.total_tokens or 0
    total_cost = openai_service.calculate_cost(total_tokens, church.gpt_model or "gpt-4o-mini")
    
    return {
        "success": True,
        "data": {
            "id": church.id,
            "name": church.name,
            "subscription_plan": church.subscription_plan,
            "max_agents": church.max_agents,
            "current_agents_count": agents_count,
            "gpt_api_configured": bool(church.gpt_api_key),
            "database_connected": bool(db_config),
            "last_sync": db_config.last_sync if db_config else None,
            "monthly_usage": {
                "total_tokens": total_tokens,
                "total_requests": total_requests,
                "total_cost": round(total_cost, 2),
                "remaining_quota": max(0, (church.monthly_token_limit or 100000) - total_tokens)
            }
        }
    }


@router.get("/gpt-config", response_model=dict)
def read_gpt_config(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get GPT API configuration.
    """
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    return {
        "success": True,
        "data": {
            "api_key": "sk-..." if church.gpt_api_key else None,
            "database_connected": bool(church.gpt_api_key),
            "last_sync": church.gpt_last_test,
            "model": church.gpt_model or "gpt-4o-mini",
            "max_tokens": church.max_tokens or 2000,
            "temperature": church.temperature or 0.7,
            "is_active": bool(church.gpt_api_key)
        }
    }


@router.put("/gpt-config", response_model=dict)
async def update_gpt_config(
    *,
    db: Session = Depends(deps.get_db),
    config_in: GPTConfigUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update GPT API configuration.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins can update GPT configuration"
        )
    
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    # Test API key if provided
    if config_in.api_key:
        test_result = await openai_service.test_connection(config_in.api_key)
        if not test_result:
            raise HTTPException(
                status_code=400,
                detail="Invalid OpenAI API key"
            )
        
        # Store API key (temporarily without encryption for testing)
        # TODO: Re-enable encryption after fixing server ENCRYPTION_KEY
        church.gpt_api_key = config_in.api_key  # encrypt_data(config_in.api_key)
    
    # Update other settings
    if config_in.model:
        church.gpt_model = config_in.model
    if config_in.max_tokens:
        church.max_tokens = config_in.max_tokens
    if config_in.temperature is not None:
        church.temperature = config_in.temperature
    
    db.commit()
    db.refresh(church)
    
    return {
        "success": True,
        "message": "GPT configuration updated successfully"
    }


@router.get("/system-status", response_model=dict)
def read_system_status(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get system status including GPT API, database, and agents.
    """
    church = db.query(Church).filter(
        Church.id == current_user.church_id
    ).first()
    
    if not church:
        raise HTTPException(
            status_code=404,
            detail="Church not found"
        )
    
    # GPT API status
    gpt_status = {
        "configured": bool(church.gpt_api_key),
        "model": church.gpt_model or "gpt-4o-mini",
        "last_test": church.gpt_last_test,
        "status": "active" if church.gpt_api_key else "not_configured"
    }
    
    # Database status
    db_config = db.query(ChurchDatabaseConfig).filter(
        ChurchDatabaseConfig.church_id == church.id,
        ChurchDatabaseConfig.is_active == True
    ).first()
    
    database_status = {
        "connected": bool(db_config),
        "last_sync": db_config.last_sync if db_config else None,
        "tables_count": db_config.tables_count if db_config else 0,
        "status": "healthy" if db_config and db_config.is_active else "disconnected"
    }
    
    # Agents status
    agents = db.query(AIAgent).filter(
        AIAgent.church_id == church.id
    ).all()
    
    active_agents = sum(1 for agent in agents if agent.is_active)
    total_tokens = sum(agent.total_tokens_used or 0 for agent in agents)
    total_cost = sum(agent.total_cost or 0 for agent in agents)
    
    agents_status = {
        "total": len(agents),
        "active": active_agents,
        "total_tokens_this_month": church.current_month_tokens or 0,
        "total_cost_this_month": church.current_month_cost or 0
    }
    
    return {
        "success": True,
        "data": {
            "gpt_api": gpt_status,
            "database": database_status,
            "agents": agents_status
        }
    }


@router.post("/database/config", response_model=ChurchDatabaseConfigSchema)
async def create_database_config(
    *,
    db: Session = Depends(deps.get_db),
    config_in: ChurchDatabaseConfigCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Configure church database connection.
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Only admins can configure database connection"
        )
    
    # Check if config already exists
    existing_config = db.query(ChurchDatabaseConfig).filter(
        ChurchDatabaseConfig.church_id == current_user.church_id
    ).first()
    
    if existing_config:
        # Update existing config
        for field, value in config_in.dict().items():
            if field == "password" and value:
                setattr(existing_config, field, encrypt_data(value))
            else:
                setattr(existing_config, field, value)
        
        # Test connection
        test_result = await church_data_service.test_connection(existing_config)
        existing_config.is_active = test_result["connected"]
        existing_config.tables_count = len(test_result.get("tables_found", []))
        
        db.commit()
        db.refresh(existing_config)
        
        return existing_config
    else:
        # Create new config
        config_dict = config_in.dict()
        if config_dict.get("password"):
            config_dict["password"] = encrypt_data(config_dict["password"])
        
        config = ChurchDatabaseConfig(
            **config_dict,
            church_id=current_user.church_id
        )
        
        # Test connection
        test_result = await church_data_service.test_connection(config)
        config.is_active = test_result["connected"]
        config.tables_count = len(test_result.get("tables_found", []))
        
        db.add(config)
        db.commit()
        db.refresh(config)
        
        return config


@router.get("/database/test-connection", response_model=dict)
async def test_database_connection(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Test church database connection.
    """
    config = db.query(ChurchDatabaseConfig).filter(
        ChurchDatabaseConfig.church_id == current_user.church_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404,
            detail="No database configuration found"
        )
    
    test_result = await church_data_service.test_connection(config)
    
    # Update last sync if successful
    if test_result["connected"]:
        config.last_sync = datetime.now()
        config.is_active = True
        config.tables_count = len(test_result.get("tables_found", []))
        db.commit()
    
    return {
        "success": True,
        "data": test_result
    }


@router.post("/database/query", response_model=dict)
async def query_church_database(
    *,
    db: Session = Depends(deps.get_db),
    query_params: dict,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Query church database (internal API for AI agents).
    """
    query_type = query_params.get("query_type")
    parameters = query_params.get("parameters", {})
    
    if query_type == "members_absent":
        result = await church_data_service.query_members_absent(
            church_id=current_user.church_id,
            weeks=parameters.get("weeks", 4),
            service_type=parameters.get("service_type", "sunday"),
            db=db
        )
    elif query_type == "attendance_stats":
        result = await church_data_service.query_attendance_stats(
            church_id=current_user.church_id,
            period=parameters.get("period", "month"),
            db=db
        )
    elif query_type == "member_info":
        result = await church_data_service.query_member_info(
            church_id=current_user.church_id,
            search_term=parameters.get("search_term"),
            db=db
        )
    elif query_type == "donation_stats":
        result = await church_data_service.query_donation_stats(
            church_id=current_user.church_id,
            period=parameters.get("period", "month"),
            db=db
        )
    elif query_type == "events":
        result = await church_data_service.query_events(
            church_id=current_user.church_id,
            upcoming=parameters.get("upcoming", True),
            db=db
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown query type: {query_type}"
        )
    
    return {
        "success": True,
        "data": result
    }