from typing import Any, List, Optional
from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract

from app import models, schemas
from app.api import deps

router = APIRouter()


# Donor endpoints
@router.get("/donors", response_model=List[schemas.financial.Donor])
def get_donors(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all donors for the current user's church"""
    donors = db.query(models.Donor).join(
        models.Member, models.Donor.member_id == models.Member.id
    ).filter(
        models.Member.church_id == current_user.church_id
    ).offset(skip).limit(limit).all()
    return donors


@router.post("/donors", response_model=schemas.financial.Donor)
def create_donor(
    *,
    db: Session = Depends(deps.get_db),
    donor_in: schemas.financial.DonorCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create a new donor"""
    # Verify member belongs to user's church if member_id is provided
    if donor_in.member_id:
        member = db.query(models.Member).filter(
            models.Member.id == donor_in.member_id,
            models.Member.church_id == current_user.church_id
        ).first()
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )
    
    donor = models.Donor(**donor_in.dict())
    db.add(donor)
    db.commit()
    db.refresh(donor)
    return donor


@router.get("/donors/{donor_id}", response_model=schemas.financial.Donor)
def get_donor(
    donor_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Get a specific donor"""
    donor = db.query(models.Donor).join(
        models.Member, models.Donor.member_id == models.Member.id
    ).filter(
        models.Donor.id == donor_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    return donor


# Offering endpoints
@router.get("/offerings", response_model=List[schemas.financial.Offering])
def get_offerings(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    donor_id: Optional[int] = Query(None),
    fund_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """Get offerings with optional filters"""
    query = db.query(models.Offering).filter(
        models.Offering.church_id == current_user.church_id
    )
    
    if donor_id:
        query = query.filter(models.Offering.donor_id == donor_id)
    if fund_type:
        query = query.filter(models.Offering.fund_type == fund_type)
    if start_date:
        query = query.filter(models.Offering.offered_on >= start_date)
    if end_date:
        query = query.filter(models.Offering.offered_on <= end_date)
    
    offerings = query.order_by(models.Offering.offered_on.desc()).offset(skip).limit(limit).all()
    return offerings


@router.post("/offerings", response_model=schemas.financial.Offering)
def create_offering(
    *,
    db: Session = Depends(deps.get_db),
    offering_in: schemas.financial.OfferingCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create a new offering record"""
    # Verify donor exists and belongs to user's church
    donor = db.query(models.Donor).join(
        models.Member, models.Donor.member_id == models.Member.id
    ).filter(
        models.Donor.id == offering_in.donor_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    offering_data = offering_in.dict()
    offering_data["input_user_id"] = current_user.id
    offering = models.Offering(**offering_data)
    db.add(offering)
    db.commit()
    db.refresh(offering)
    return offering


# Fund Type endpoints
@router.get("/fund-types", response_model=List[schemas.financial.FundType])
def get_fund_types(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    is_active: Optional[bool] = Query(True)
):
    """Get fund types for the current user's church"""
    query = db.query(models.FundType).filter(
        models.FundType.church_id == current_user.church_id
    )
    
    if is_active is not None:
        query = query.filter(models.FundType.is_active == is_active)
    
    fund_types = query.order_by(models.FundType.sort_order, models.FundType.name).all()
    return fund_types


@router.post("/fund-types", response_model=schemas.financial.FundType)
def create_fund_type(
    *,
    db: Session = Depends(deps.get_db),
    fund_type_in: schemas.financial.FundTypeCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create a new fund type"""
    # Check if code already exists for this church
    existing = db.query(models.FundType).filter(
        models.FundType.church_id == current_user.church_id,
        models.FundType.code == fund_type_in.code
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fund type code already exists"
        )
    
    fund_type_data = fund_type_in.dict()
    fund_type_data["church_id"] = current_user.church_id
    fund_type = models.FundType(**fund_type_data)
    db.add(fund_type)
    db.commit()
    db.refresh(fund_type)
    return fund_type


# Receipt endpoints
@router.get("/receipts", response_model=List[schemas.financial.Receipt])
def get_receipts(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    tax_year: Optional[int] = Query(None),
    donor_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100
):
    """Get receipts with optional filters"""
    query = db.query(models.Receipt).filter(
        models.Receipt.church_id == current_user.church_id
    )
    
    if tax_year:
        query = query.filter(models.Receipt.tax_year == tax_year)
    if donor_id:
        query = query.filter(models.Receipt.donor_id == donor_id)
    
    receipts = query.order_by(models.Receipt.issued_at.desc()).offset(skip).limit(limit).all()
    return receipts


@router.post("/receipts", response_model=schemas.financial.Receipt)
def create_receipt(
    *,
    db: Session = Depends(deps.get_db),
    receipt_in: schemas.financial.ReceiptCreate,
    current_user: models.User = Depends(deps.get_current_active_user)
):
    """Create a new receipt"""
    # Verify donor exists and belongs to user's church
    donor = db.query(models.Donor).join(
        models.Member, models.Donor.member_id == models.Member.id
    ).filter(
        models.Donor.id == receipt_in.donor_id,
        models.Member.church_id == current_user.church_id
    ).first()
    
    if not donor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Donor not found"
        )
    
    receipt_data = receipt_in.dict()
    receipt_data["church_id"] = current_user.church_id
    receipt_data["issued_by"] = current_user.id
    receipt_data["issued_at"] = datetime.now()
    
    receipt = models.Receipt(**receipt_data)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


# Statistics endpoints
@router.get("/statistics/offerings-summary", response_model=List[schemas.financial.OfferingSummary])
def get_offerings_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: date = Query(...),
    end_date: date = Query(...),
    group_by: str = Query("fund_type", regex="^(fund_type|month)$")
):
    """Get offering statistics summary"""
    if group_by == "fund_type":
        # Group by fund type
        results = db.query(
            models.Offering.fund_type,
            func.sum(models.Offering.amount).label('total_amount'),
            func.count(models.Offering.id).label('offering_count')
        ).filter(
            models.Offering.church_id == current_user.church_id,
            models.Offering.offered_on >= start_date,
            models.Offering.offered_on <= end_date
        ).group_by(models.Offering.fund_type).all()
        
        return [
            schemas.financial.OfferingSummary(
                fund_type=result.fund_type,
                total_amount=result.total_amount,
                offering_count=result.offering_count,
                period_start=start_date,
                period_end=end_date
            )
            for result in results
        ]
    
    elif group_by == "month":
        # Group by month
        results = db.query(
            extract('year', models.Offering.offered_on).label('year'),
            extract('month', models.Offering.offered_on).label('month'),
            func.sum(models.Offering.amount).label('total_amount'),
            func.count(models.Offering.id).label('offering_count')
        ).filter(
            models.Offering.church_id == current_user.church_id,
            models.Offering.offered_on >= start_date,
            models.Offering.offered_on <= end_date
        ).group_by(
            extract('year', models.Offering.offered_on),
            extract('month', models.Offering.offered_on)
        ).order_by(
            extract('year', models.Offering.offered_on),
            extract('month', models.Offering.offered_on)
        ).all()
        
        return [
            schemas.financial.OfferingSummary(
                fund_type=f"{int(result.year)}-{int(result.month):02d}",
                total_amount=result.total_amount,
                offering_count=result.offering_count,
                period_start=start_date,
                period_end=end_date
            )
            for result in results
        ]


@router.get("/statistics/donor-summary", response_model=List[schemas.financial.DonorSummary])
def get_donor_summary(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    start_date: date = Query(...),
    end_date: date = Query(...),
    limit: int = Query(50, le=100)
):
    """Get top donors summary"""
    results = db.query(
        models.Donor.id,
        models.Donor.legal_name,
        func.sum(models.Offering.amount).label('total_amount'),
        func.count(models.Offering.id).label('offering_count'),
        func.array_agg(models.Offering.fund_type.distinct()).label('fund_types')
    ).join(
        models.Offering, models.Donor.id == models.Offering.donor_id
    ).join(
        models.Member, models.Donor.member_id == models.Member.id
    ).filter(
        models.Member.church_id == current_user.church_id,
        models.Offering.offered_on >= start_date,
        models.Offering.offered_on <= end_date
    ).group_by(
        models.Donor.id, models.Donor.legal_name
    ).order_by(
        func.sum(models.Offering.amount).desc()
    ).limit(limit).all()
    
    return [
        schemas.financial.DonorSummary(
            donor_id=result.id,
            donor_name=result.legal_name,
            total_amount=result.total_amount,
            offering_count=result.offering_count,
            fund_types=result.fund_types or []
        )
        for result in results
    ]