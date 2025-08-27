from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
from pathlib import Path
import logging
from app.api import deps
from app import models

router = APIRouter()
logger = logging.getLogger(__name__)

# Get the templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page - requires superuser authentication"""
    return templates.TemplateResponse("admin.html", {"request": request})


@router.post("/admin/migrate-secretary-agents")
async def migrate_secretary_agents(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """Apply secretary agent database migration and create agents for existing churches"""
    try:
        logger.info("Starting secretary agent migration...")
        
        # Import services here to avoid circular imports
        from app.services.secretary_agent_service import secretary_agent_service
        from app.models.church import Church
        from app.models.ai_agent import AIAgent
        from sqlalchemy import text
        
        results = {
            "migration_applied": False,
            "churches_processed": 0,
            "agents_created": 0,
            "agents_skipped": 0,
            "errors": []
        }
        
        # Step 1: Check if migration columns exist
        try:
            # Try to query the new columns
            db.execute(text("SELECT is_default, enable_church_data, created_by_system FROM ai_agents LIMIT 1"))
            results["migration_applied"] = True
            logger.info("Migration columns already exist")
        except Exception as e:
            logger.info(f"Migration columns don't exist: {e}")
            # Try to apply the migration manually
            try:
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN is_default BOOLEAN DEFAULT FALSE NOT NULL"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN enable_church_data BOOLEAN DEFAULT FALSE NOT NULL"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN created_by_system BOOLEAN DEFAULT FALSE NOT NULL"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN gpt_model VARCHAR(50)"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN max_tokens INTEGER"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN temperature FLOAT"))
                db.commit()
                results["migration_applied"] = True
                logger.info("Migration columns added successfully")
            except Exception as migration_error:
                logger.error(f"Failed to apply migration: {migration_error}")
                results["errors"].append(f"Migration failed: {str(migration_error)}")
        
        # Step 2: Create secretary agents for existing churches
        if results["migration_applied"]:
            churches = db.query(Church).all()
            results["churches_processed"] = len(churches)
            
            for church in churches:
                try:
                    # Check if church already has secretary agent
                    existing_secretary = db.query(AIAgent).filter(
                        AIAgent.church_id == church.id,
                        AIAgent.category == "secretary"
                    ).first()
                    
                    if existing_secretary:
                        results["agents_skipped"] += 1
                        logger.info(f"Church {church.id} already has secretary agent")
                        continue
                    
                    # Create secretary agent
                    secretary_agent = secretary_agent_service.ensure_church_secretary_agent(
                        church.id, db
                    )
                    results["agents_created"] += 1
                    logger.info(f"Created secretary agent {secretary_agent.id} for church {church.id}")
                    
                except Exception as e:
                    error_msg = f"Failed to create secretary agent for church {church.id}: {str(e)}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
        
        logger.info(f"Migration completed: {results}")
        return {
            "success": True,
            "message": "Secretary agent migration completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return {
            "success": False,
            "message": f"Migration failed: {str(e)}"
        }


@router.post("/migrate-urgent")
async def migrate_urgent(db: Session = Depends(deps.get_db)):
    """Emergency migration endpoint - no authentication required"""
    try:
        from app.services.secretary_agent_service import secretary_agent_service
        from app.models.church import Church
        from app.models.ai_agent import AIAgent
        from sqlalchemy import text
        
        logger.info("Starting urgent secretary agent migration...")
        
        # Step 1: Apply database migration
        try:
            db.execute(text("SELECT is_default FROM ai_agents LIMIT 1"))
            logger.info("Migration already applied")
        except:
            logger.info("Applying migration...")
            try:
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN is_default BOOLEAN DEFAULT FALSE NOT NULL"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN enable_church_data BOOLEAN DEFAULT FALSE NOT NULL"))  
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN created_by_system BOOLEAN DEFAULT FALSE NOT NULL"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN gpt_model VARCHAR(50)"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN max_tokens INTEGER"))
                db.execute(text("ALTER TABLE ai_agents ADD COLUMN temperature FLOAT"))
                db.commit()
                logger.info("Migration applied successfully")
            except Exception as e:
                logger.error(f"Migration failed: {e}")
                return {"success": False, "error": str(e)}
        
        # Step 2: Create secretary agents
        churches = db.query(Church).all()
        created = 0
        
        for church in churches:
            try:
                existing = db.query(AIAgent).filter(
                    AIAgent.church_id == church.id,
                    AIAgent.category == "secretary"
                ).first()
                
                if not existing:
                    secretary_agent_service.ensure_church_secretary_agent(church.id, db)
                    created += 1
                    logger.info(f"Created secretary agent for church {church.id}")
            except Exception as e:
                logger.error(f"Failed for church {church.id}: {e}")
        
        return {
            "success": True,
            "message": f"Migration completed. Created {created} secretary agents for {len(churches)} churches."
        }
        
    except Exception as e:
        logger.error(f"Urgent migration failed: {e}")
        return {"success": False, "error": str(e)}
