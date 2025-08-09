from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app import models, schemas
from app.api import deps
from app.models.ai_agent import AIAgent, OfficialAgentTemplate
from app.schemas.ai_agent import (
    AIAgentCreate, AIAgentUpdate, AIAgent as AIAgentSchema,
    AIAgentWithStats, OfficialAgentTemplate as TemplateSchema
)

router = APIRouter()


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
    """
    # Get agents
    agents = db.query(AIAgent).filter(
        AIAgent.church_id == current_user.church_id
    ).offset(skip).limit(limit).all()
    
    # Calculate stats
    total_agents = db.query(AIAgent).filter(
        AIAgent.church_id == current_user.church_id
    ).count()
    
    active_agents = db.query(AIAgent).filter(
        AIAgent.church_id == current_user.church_id,
        AIAgent.is_active == True
    ).count()
    
    total_usage = sum(agent.usage_count for agent in agents)
    
    # Format response
    agents_data = []
    for agent in agents:
        agent_dict = {
            "id": agent.id,
            "name": agent.name,
            "category": agent.category,
            "description": agent.description,
            "detailed_description": agent.detailed_description,
            "icon": agent.icon,
            "usage": agent.usage_count,
            "is_active": agent.is_active,
            "created_at": agent.created_at,
            "updated_at": agent.updated_at,
            "total_tokens_used": agent.total_tokens_used,
            "total_cost": agent.total_cost,
            "system_prompt": agent.system_prompt,
            "template_id": agent.template_id
        }
        agents_data.append(agent_dict)
    
    return {
        "success": True,
        "data": {
            "agents": agents_data,
            "stats": {
                "total_agents": total_agents,
                "active_agents": active_agents,
                "inactive_agents": total_agents - active_agents,
                "total_usage": total_usage
            }
        }
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
            status_code=403,
            detail="Only admins and ministers can create AI agents"
        )
    
    # Check agent limit
    church = db.query(models.Church).filter(
        models.Church.id == current_user.church_id
    ).first()
    
    current_agents_count = db.query(AIAgent).filter(
        AIAgent.church_id == current_user.church_id
    ).count()
    
    if current_agents_count >= church.max_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Agent limit reached. Maximum {church.max_agents} agents allowed."
        )
    
    # If template_id is provided, copy from template
    if agent_in.template_id:
        template = db.query(OfficialAgentTemplate).filter(
            OfficialAgentTemplate.id == agent_in.template_id
        ).first()
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Template not found"
            )
        
        # Copy template values if not provided
        if not agent_in.system_prompt:
            agent_in.system_prompt = template.system_prompt
        if not agent_in.description:
            agent_in.description = template.description
        if not agent_in.detailed_description:
            agent_in.detailed_description = template.detailed_description
    
    # Create agent
    agent = AIAgent(
        **agent_in.dict(),
        church_id=current_user.church_id
    )
    
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
    templates = db.query(OfficialAgentTemplate).filter(
        OfficialAgentTemplate.is_public == True
    ).all()
    
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
            "is_official": True,
            "version": template.version,
            "created_by": template.created_by,
            "created_at": template.created_at
        }
        templates_data.append(template_dict)
    
    return {
        "success": True,
        "data": templates_data
    }


@router.get("/{agent_id}", response_model=AIAgentSchema)
def read_agent(
    *,
    db: Session = Depends(deps.get_db),
    agent_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get agent by ID.
    """
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.church_id == current_user.church_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )
    
    return agent


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
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.church_id == current_user.church_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )
    
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
    agent = db.query(AIAgent).filter(
        AIAgent.id == agent_id,
        AIAgent.church_id == current_user.church_id
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )
    
    db.delete(agent)
    db.commit()
    
    return {"success": True, "message": "Agent deleted successfully"}