from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services.church_default_agent_service import ChurchDefaultAgentService
# from app.services.secretary_agent_service import secretary_agent_service

router = APIRouter()


@router.get("/", response_model=List[schemas.Church])
def read_churches(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    churches = db.query(models.Church).offset(skip).limit(limit).all()
    return churches


@router.post("/", response_model=schemas.Church)
def create_church(
    *,
    db: Session = Depends(deps.get_db),
    church_in: schemas.ChurchCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    # Create church
    church = models.Church(**church_in.dict())
    db.add(church)
    db.commit()
    db.refresh(church)

    # Create default agent for the new church
    try:
        default_agent = ChurchDefaultAgentService.create_default_agent_for_church(
            church.id, db
        )
        print(
            f"✅ Created default agent (ID: {default_agent.id}) for new church: {church.name}"
        )
    except Exception as e:
        print(f"⚠️ Failed to create default agent for church {church.name}: {str(e)}")
        # Don't fail church creation if agent creation fails
    
    # Create secretary agent for the new church (임시 주석 처리)
    # try:
    #     secretary_agent = secretary_agent_service.ensure_church_secretary_agent(
    #         church.id, db
    #     )
    #     print(
    #         f"✅ Created secretary agent (ID: {secretary_agent.id}) for new church: {church.name}"
    #     )
    # except Exception as e:
    #     print(f"⚠️ Failed to create secretary agent for church {church.name}: {str(e)}")
    #     # Don't fail church creation if secretary agent creation fails

    return church


@router.get("/my", response_model=schemas.Church)
def read_my_church(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    if not current_user.church_id:
        raise HTTPException(
            status_code=404, detail="User not associated with any church"
        )

    church = (
        db.query(models.Church)
        .filter(models.Church.id == current_user.church_id)
        .first()
    )
    if not church:
        raise HTTPException(status_code=404, detail="Church not found")

    return church


@router.get("/{church_id}", response_model=schemas.Church)
def read_church(
    *,
    db: Session = Depends(deps.get_db),
    church_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    if not church:
        raise HTTPException(status_code=404, detail="Church not found")

    if not current_user.is_superuser and church.id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return church


@router.put("/{church_id}", response_model=schemas.Church)
def update_church(
    *,
    db: Session = Depends(deps.get_db),
    church_id: int,
    church_in: schemas.ChurchUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    church = db.query(models.Church).filter(models.Church.id == church_id).first()
    if not church:
        raise HTTPException(status_code=404, detail="Church not found")

    if not current_user.is_superuser and church.id != current_user.church_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    update_data = church_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(church, field, value)

    db.add(church)
    db.commit()
    db.refresh(church)
    return church
