from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.CalendarEvent])
def get_calendar_events(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    event_type: Optional[str] = Query(None, description="Event type filter"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve calendar events.
    """
    query = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.church_id == current_user.church_id
    )
    
    if start_date:
        query = query.filter(models.CalendarEvent.event_date >= start_date)
    
    if end_date:
        query = query.filter(models.CalendarEvent.event_date <= end_date)
    
    if event_type:
        query = query.filter(models.CalendarEvent.event_type == event_type)
    
    events = query.offset(skip).limit(limit).all()
    return events


@router.post("/", response_model=schemas.CalendarEvent)
def create_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_in: schemas.CalendarEventCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new calendar event.
    """
    event = models.CalendarEvent(
        **event_in.dict(),
        church_id=current_user.church_id,
        created_by=current_user.id
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.put("/{event_id}", response_model=schemas.CalendarEvent)
def update_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    event_in: schemas.CalendarEventUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update calendar event.
    """
    event = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.id == event_id,
        models.CalendarEvent.church_id == current_user.church_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}")
def delete_calendar_event(
    *,
    db: Session = Depends(deps.get_db),
    event_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete calendar event.
    """
    event = db.query(models.CalendarEvent).filter(
        models.CalendarEvent.id == event_id,
        models.CalendarEvent.church_id == current_user.church_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    
    return {"message": "Event deleted successfully"}


@router.get("/birthdays", response_model=List[dict])
def get_upcoming_birthdays(
    db: Session = Depends(deps.get_db),
    days_ahead: int = Query(30, description="Number of days to look ahead"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get upcoming birthdays.
    """
    today = datetime.utcnow().date()
    end_date = today + timedelta(days=days_ahead)
    
    members = db.query(models.Member).filter(
        models.Member.church_id == current_user.church_id,
        models.Member.birthdate.isnot(None)
    ).all()
    
    upcoming_birthdays = []
    
    for member in members:
        if not member.birthdate:
            continue
        
        # Calculate this year's birthday
        this_year_birthday = member.birthdate.replace(year=today.year)
        
        # If birthday already passed this year, check next year
        if this_year_birthday < today:
            next_year_birthday = member.birthdate.replace(year=today.year + 1)
            if next_year_birthday <= end_date:
                upcoming_birthdays.append({
                    "member_id": member.id,
                    "member_name": member.name,
                    "birthday": next_year_birthday,
                    "age": today.year + 1 - member.birthdate.year,
                    "days_until": (next_year_birthday - today).days
                })
        elif this_year_birthday <= end_date:
            upcoming_birthdays.append({
                "member_id": member.id,
                "member_name": member.name,
                "birthday": this_year_birthday,
                "age": today.year - member.birthdate.year,
                "days_until": (this_year_birthday - today).days
            })
    
    # Sort by days until birthday
    upcoming_birthdays.sort(key=lambda x: x["days_until"])
    
    return upcoming_birthdays


@router.post("/birthdays/create-events")
def create_birthday_events(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create calendar events for all member birthdays.
    """
    members = db.query(models.Member).filter(
        models.Member.church_id == current_user.church_id,
        models.Member.birthdate.isnot(None)
    ).all()
    
    created_count = 0
    
    for member in members:
        if not member.birthdate:
            continue
        
        # Check if birthday event already exists
        existing_event = db.query(models.CalendarEvent).filter(
            models.CalendarEvent.church_id == current_user.church_id,
            models.CalendarEvent.event_type == "birthday",
            models.CalendarEvent.related_member_id == member.id
        ).first()
        
        if not existing_event:
            # Create recurring birthday event
            event = models.CalendarEvent(
                church_id=current_user.church_id,
                title=f"{member.name}님 생일",
                description=f"{member.name}님의 생일입니다.",
                event_type="birthday",
                event_date=member.birthdate,
                is_recurring=True,
                recurrence_pattern="yearly",
                related_member_id=member.id,
                created_by=current_user.id
            )
            db.add(event)
            created_count += 1
    
    db.commit()
    
    return {
        "message": f"Created {created_count} birthday events",
        "total_members_with_birthdays": len(members),
        "created_count": created_count
    }