from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app import models, schemas
from app.api import deps
from app.models.ai_agent import AIAgent, OfficialAgentTemplate
from app.services.church_default_agent_service import ChurchDefaultAgentService
# from app.services.secretary_agent_service import secretary_agent_service
from app.schemas.ai_agent import (
    AIAgentCreate,
    AIAgentUpdate,
    AIAgent as AIAgentSchema,
    AIAgentWithStats,
    OfficialAgentTemplate as TemplateSchema,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/templates", response_model=dict)
def read_agent_templates(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve official agent templates.
    """
    # For now, return empty templates if table doesn't exist
    try:
        templates = (
            db.query(OfficialAgentTemplate)
            .filter(OfficialAgentTemplate.is_public == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    except Exception as e:
        logger.warning(f"Failed to fetch templates: {e}")
        templates = []

    templates_data = []
    for template in templates:
        templates_data.append(
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category,
                "system_prompt": template.system_prompt,
                "icon": template.icon,
                "config": {
                    "model": "gpt-4o-mini",  # Default model for templates
                    "temperature": 0.7,     # Default temperature
                    "max_tokens": 4000,     # Default max tokens
                },
            }
        )

    return {"success": True, "templates": templates_data}


@router.get("/", response_model=dict)
def read_agents(
    *,
    db: Session = Depends(deps.get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve AI agents for the current user's church.
    Always includes the global default agent (ID: 0).
    """
    # Get all agents for this church
    # Ensure church has at least one default agent (임시 주석 처리)
    # ChurchDefaultAgentService.ensure_church_has_default_agent(
    #     current_user.church_id, db
    # )
    
    # Ensure church has secretary agent
    # secretary_agent_service.ensure_church_secretary_agent(
    #     current_user.church_id, db
    # )

    # Get all church agents
    db_agents = (
        db.query(AIAgent).filter(AIAgent.church_id == current_user.church_id).all()
    )

    # Apply pagination
    paginated_agents = db_agents[skip : skip + limit]

    # Calculate stats
    total_agents = len(db_agents)
    active_agents = len([a for a in db_agents if a.is_active])
    total_usage = sum(agent.usage_count or 0 for agent in paginated_agents)

    # Format agent data for response
    formatted_agents = []
    for agent in paginated_agents:
        agent_dict = {
            "id": agent.id,
            "name": agent.name,
            "category": agent.category,
            "description": agent.description,
            "detailed_description": agent.detailed_description,
            "icon": agent.icon,
            "usage": agent.usage_count or 0,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
            "total_tokens_used": agent.total_tokens_used or 0,
            "total_cost": agent.total_cost or 0.0,
            "system_prompt": agent.system_prompt,
            "template_id": agent.template_id,
            "church_data_sources": agent.church_data_sources or {},
        }
        formatted_agents.append(agent_dict)

    return {
        "success": True,
        "data": {
            "agents": formatted_agents,
            "stats": {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "inactive_agents": total_agents - active_agents,
                "total_usage": total_usage,
            },
        },
    }


@router.post("/", response_model=AIAgentSchema)
def create_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_in: AIAgentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new AI agent.
    """
    # Check if user has permission
    if current_user.role not in ["admin", "minister"]:
        raise HTTPException(
            status_code=403, detail="Only admins and ministers can create AI agents"
        )

    # Check agent limit
    church = (
        db.query(models.Church)
        .filter(models.Church.id == current_user.church_id)
        .first()
    )

    current_agents_count = (
        db.query(AIAgent).filter(AIAgent.church_id == current_user.church_id).count()
    )

    # Handle None value for max_agents (default to 10 if not set)
    max_agents = church.max_agents if church.max_agents is not None else 10

    if current_agents_count >= max_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Agent limit reached. Maximum {max_agents} agents allowed.",
        )

    # If template_id is provided, copy from template
    if agent_in.template_id:
        template = (
            db.query(OfficialAgentTemplate)
            .filter(OfficialAgentTemplate.id == agent_in.template_id)
            .first()
        )

        if not template:
            raise HTTPException(status_code=404, detail="Template not found")

        # Copy template values if not provided
        if not agent_in.system_prompt:
            agent_in.system_prompt = template.system_prompt
        if not agent_in.description:
            agent_in.description = template.description
        if not agent_in.detailed_description:
            agent_in.detailed_description = template.detailed_description

    # Create agent
    agent_dict = agent_in.dict()
    # Ensure church_data_sources is properly formatted
    if "church_data_sources" in agent_dict and agent_dict["church_data_sources"]:
        # Convert ChurchDataSources model to dict if needed
        if hasattr(agent_dict["church_data_sources"], "dict"):
            agent_dict["church_data_sources"] = agent_dict["church_data_sources"].dict()
    else:
        agent_dict["church_data_sources"] = {}

    agent = AIAgent(**agent_dict, church_id=current_user.church_id)

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


@router.get("/templates/official", response_model=dict)
def read_official_templates(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get official agent templates.
    """
    templates = (
        db.query(OfficialAgentTemplate)
        .filter(OfficialAgentTemplate.is_public == True)
        .all()
    )

    templates_data = []
    for template in templates:
        template_dict = {
            "id": template.id,
            "name": template.name,
            "category": template.category,
            "description": template.description,
            "detailed_description": template.detailed_description,
            "icon": template.icon,
            "system_prompt": template.system_prompt,
            "church_data_sources": (
                template.church_data_sources if template.church_data_sources else {}
            ),
            "is_official": True,
            "version": template.version,
            "created_by": template.created_by,
            "created_at": template.created_at,
        }
        templates_data.append(template_dict)

    return {"success": True, "data": templates_data}


@router.get("/{agent_id}", response_model=dict)
def read_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get agent by ID. Church-specific agents only.
    """
    # Get church-specific agent
    agent = (
        db.query(AIAgent)
        .filter(AIAgent.id == agent_id, AIAgent.church_id == current_user.church_id)
        .first()
    )

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Format agent data
    agent_data = {
        "id": agent.id,
        "church_id": agent.church_id,
        "template_id": agent.template_id,
        "name": agent.name,
        "category": agent.category,
        "description": agent.description,
        "detailed_description": agent.detailed_description,
        "icon": agent.icon,
        "system_prompt": agent.system_prompt,
        "church_data_sources": agent.church_data_sources or {},
        "is_active": agent.is_active,
        "usage_count": agent.usage_count or 0,
        "total_tokens_used": agent.total_tokens_used or 0,
        "total_cost": agent.total_cost or 0.0,
        "created_at": agent.created_at,
        "updated_at": agent.updated_at,
    }

    return {"success": True, "data": agent_data}


@router.put("/{agent_id}", response_model=AIAgentSchema)
def update_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    agent_in: AIAgentUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update AI agent.
    """
    agent = (
        db.query(AIAgent)
        .filter(AIAgent.id == agent_id, AIAgent.church_id == current_user.church_id)
        .first()
    )

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Update agent
    update_data = agent_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)

    return agent


@router.delete("/{agent_id}")
def delete_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete AI agent.
    """
    agent = (
        db.query(AIAgent)
        .filter(AIAgent.id == agent_id, AIAgent.church_id == current_user.church_id)
        .first()
    )

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    db.delete(agent)
    db.commit()

    return {"success": True, "message": "Agent deleted successfully"}
