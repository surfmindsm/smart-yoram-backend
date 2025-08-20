from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app import models, schemas
from app.api import deps
from app.core.config import settings

router = APIRouter()


@router.post("/send", response_model=schemas.SMS)
def send_sms(
    *,
    db: Session = Depends(deps.get_db),
    sms_in: schemas.SMSCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Send SMS to a single recipient.
    """
    # Create SMS history record
    sms_history = models.SMSHistory(
        church_id=current_user.church_id,
        sender_id=current_user.id,
        recipient_phone=sms_in.recipient_phone,
        recipient_member_id=sms_in.recipient_member_id,
        message=sms_in.message,
        sms_type=sms_in.sms_type,
        status="pending",
    )
    db.add(sms_history)
    db.commit()

    # Send SMS (placeholder - implement actual SMS service)
    try:
        # result = sms_utils.send_sms(sms_in.recipient_phone, sms_in.message)
        # For now, simulate success
        sms_history.status = "sent"
        sms_history.sent_at = datetime.utcnow()
    except Exception as e:
        sms_history.status = "failed"
        sms_history.error_message = str(e)

    db.commit()
    db.refresh(sms_history)

    return sms_history


@router.post("/send-bulk", response_model=List[schemas.SMS])
def send_bulk_sms(
    *,
    db: Session = Depends(deps.get_db),
    sms_in: schemas.SMSBulkCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Send SMS to multiple recipients.
    """
    sms_results = []

    for member_id in sms_in.recipient_member_ids:
        member = db.query(models.Member).filter(models.Member.id == member_id).first()
        if not member or not member.phone:
            continue

        if member.church_id != current_user.church_id:
            continue

        # Create SMS history record
        sms_history = models.SMSHistory(
            church_id=current_user.church_id,
            sender_id=current_user.id,
            recipient_phone=member.phone,
            recipient_member_id=member_id,
            message=sms_in.message,
            sms_type=sms_in.sms_type,
            status="pending",
        )
        db.add(sms_history)
        db.commit()

        # Send SMS (placeholder)
        try:
            # result = sms_utils.send_sms(member.phone, sms_in.message)
            sms_history.status = "sent"
            sms_history.sent_at = datetime.utcnow()
        except Exception as e:
            sms_history.status = "failed"
            sms_history.error_message = str(e)

        db.commit()
        db.refresh(sms_history)
        sms_results.append(sms_history)

    return sms_results


@router.get("/history", response_model=List[schemas.SMS])
def get_sms_history(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve SMS history.
    """
    sms_history = (
        db.query(models.SMSHistory)
        .filter(models.SMSHistory.church_id == current_user.church_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return sms_history


@router.get("/templates")
def get_sms_templates(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get predefined SMS templates.
    """
    templates = [
        {
            "id": 1,
            "name": "주일예배 안내",
            "message": "[{church_name}] 안녕하세요 {name}님! 이번 주일예배에 참석하여 은혜받는 시간 되시길 바랍니다.",
        },
        {
            "id": 2,
            "name": "생일 축하",
            "message": "[{church_name}] {name}님의 생일을 축하합니다! 하나님의 은혜가 늘 함께하시길 기도합니다.",
        },
        {
            "id": 3,
            "name": "심방 안내",
            "message": "[{church_name}] {name}님 댁에 {date} {time}에 심방 예정입니다. 준비 부탁드립니다.",
        },
        {
            "id": 4,
            "name": "교회 행사 안내",
            "message": "[{church_name}] {event_name} 행사가 {date}에 있습니다. 많은 참석 부탁드립니다.",
        },
    ]
    return templates
