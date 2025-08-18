from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app import models, schemas
from app.api import deps
from app.core.security import get_current_active_user

router = APIRouter()


# Enhanced Member endpoints with all related data
@router.get("/{member_id}/enhanced", response_model=schemas.member_enhanced.MemberEnhanced)
def get_member_enhanced(
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get member with all enhanced data (contacts, addresses, ministries, etc.)"""
    member = db.query(models.Member).options(
        joinedload(models.Member.contacts),
        joinedload(models.Member.member_addresses).joinedload(models.MemberAddress.address),
        joinedload(models.Member.vehicles),
        joinedload(models.Member.ministries),
        joinedload(models.Member.sacraments),
        joinedload(models.Member.marriage_records),
        joinedload(models.Member.transfers),
        joinedload(models.Member.status_history)
    ).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return member


# Member Contact endpoints
@router.get("/{member_id}/contacts", response_model=List[schemas.member_enhanced.MemberContact])
def get_member_contacts(
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all contacts for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    contacts = db.query(models.MemberContact).filter(
        models.MemberContact.member_id == member_id
    ).all()
    
    return contacts


@router.post("/{member_id}/contacts", response_model=schemas.member_enhanced.MemberContact)
def create_member_contact(
    member_id: int,
    *,
    db: Session = Depends(deps.get_db),
    contact_in: schemas.member_enhanced.MemberContactCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new contact for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    contact_data = contact_in.dict()
    contact_data["member_id"] = member_id
    contact = models.MemberContact(**contact_data)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


# Member Ministry endpoints
@router.get("/{member_id}/ministries", response_model=List[schemas.member_enhanced.MemberMinistry])
def get_member_ministries(
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all ministry positions for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    ministries = db.query(models.MemberMinistry).filter(
        models.MemberMinistry.member_id == member_id
    ).order_by(models.MemberMinistry.appointed_on.desc()).all()
    
    return ministries


@router.post("/{member_id}/ministries", response_model=schemas.member_enhanced.MemberMinistry)
def create_member_ministry(
    member_id: int,
    *,
    db: Session = Depends(deps.get_db),
    ministry_in: schemas.member_enhanced.MemberMinistryCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new ministry position for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    ministry_data = ministry_in.dict()
    ministry_data["member_id"] = member_id
    ministry = models.MemberMinistry(**ministry_data)
    db.add(ministry)
    db.commit()
    db.refresh(ministry)
    return ministry


# Sacrament endpoints
@router.get("/{member_id}/sacraments", response_model=List[schemas.member_enhanced.Sacrament])
def get_member_sacraments(
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all sacraments for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    sacraments = db.query(models.Sacrament).filter(
        models.Sacrament.member_id == member_id
    ).order_by(models.Sacrament.date).all()
    
    return sacraments


@router.post("/{member_id}/sacraments", response_model=schemas.member_enhanced.Sacrament)
def create_member_sacrament(
    member_id: int,
    *,
    db: Session = Depends(deps.get_db),
    sacrament_in: schemas.member_enhanced.SacramentCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Record a new sacrament for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    sacrament_data = sacrament_in.dict()
    sacrament_data["member_id"] = member_id
    sacrament = models.Sacrament(**sacrament_data)
    db.add(sacrament)
    db.commit()
    db.refresh(sacrament)
    return sacrament


# Transfer endpoints
@router.get("/{member_id}/transfers", response_model=List[schemas.member_enhanced.Transfer])
def get_member_transfers(
    member_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all transfer records for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    transfers = db.query(models.Transfer).filter(
        models.Transfer.member_id == member_id
    ).order_by(models.Transfer.date.desc()).all()
    
    return transfers


@router.post("/{member_id}/transfers", response_model=schemas.member_enhanced.Transfer)
def create_member_transfer(
    member_id: int,
    *,
    db: Session = Depends(deps.get_db),
    transfer_in: schemas.member_enhanced.TransferCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Record a new transfer for a member"""
    # Verify member belongs to user's church
    member = db.query(models.Member).filter(
        models.Member.id == member_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    transfer_data = transfer_in.dict()
    transfer_data["member_id"] = member_id
    transfer = models.Transfer(**transfer_data)
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


# Code management endpoints
@router.get("/codes", response_model=List[schemas.member_enhanced.Code])
def get_codes(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_user),
    type: Optional[str] = Query(None)
):
    """Get all codes for the church, optionally filtered by type"""
    query = db.query(models.Code).filter(
        models.Code.church_id == current_user.church_id
    )
    
    if type:
        query = query.filter(models.Code.type == type)
    
    codes = query.order_by(models.Code.type, models.Code.code).all()
    return codes


@router.post("/codes", response_model=schemas.member_enhanced.Code)
def create_code(
    *,
    db: Session = Depends(deps.get_db),
    code_in: schemas.member_enhanced.CodeCreate,
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new code"""
    # Check if code already exists for this church and type
    existing = db.query(models.Code).filter(
        models.Code.church_id == current_user.church_id,
        models.Code.type == code_in.type,
        models.Code.code == code_in.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code already exists for this type"
        )
    
    code_data = code_in.dict()
    code_data["church_id"] = current_user.church_id
    code = models.Code(**code_data)
    db.add(code)
    db.commit()
    db.refresh(code)
    return code