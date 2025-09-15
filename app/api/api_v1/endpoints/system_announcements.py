from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from datetime import date, datetime
import json

from app import models, schemas
from app.api import deps
from app.schemas import system_announcement as system_schemas

router = APIRouter()


@router.get("/", response_model=List[system_schemas.SystemAnnouncement])
def get_active_system_announcements(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    현재 유효한 시스템 공지사항 조회
    모든 사용자가 접근 가능 (각 교회 사용자들)
    """
    try:
        today = date.today()
        
        # 현재 유효한 시스템 공지사항 조회
        query = db.query(models.SystemAnnouncement).filter(
            models.SystemAnnouncement.is_active == True,
            models.SystemAnnouncement.start_date <= today,
            or_(
                models.SystemAnnouncement.end_date.is_(None),
                models.SystemAnnouncement.end_date >= today
            )
        )
        
        # 대상 교회 필터링 (target_churches가 NULL이면 모든 교회)
        announcements = []
        for announcement in query.all():
            if announcement.target_churches:
                try:
                    target_church_ids = json.loads(announcement.target_churches)
                    if current_user.church_id not in target_church_ids:
                        continue
                except:
                    # JSON 파싱 에러시 모든 교회에 표시
                    pass
            announcements.append(announcement)
        
        # 우선순위 순으로 정렬 (urgent > important > normal)
        priority_order = {'urgent': 0, 'important': 1, 'normal': 2}
        announcements.sort(
            key=lambda x: (
                priority_order.get(x.priority, 2),
                -int(x.is_pinned),
                x.created_at.timestamp() if x.created_at else 0
            ),
            reverse=True
        )
        
        return announcements[skip:skip + limit]
        
    except Exception as e:
        print(f"Error in get_active_system_announcements: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/admin")
def get_all_system_announcements_admin(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    모든 시스템 공지사항 조회 (시스템 관리자용)
    권한: church_id = 0인 사용자만
    """
    try:
        if current_user.church_id != 0:
            return {"error": "시스템 관리자만 접근 가능합니다", "announcements": []}
        
        announcements = db.query(models.SystemAnnouncement).order_by(
            desc(models.SystemAnnouncement.created_at)
        ).offset(skip).limit(limit).all()
        
        # 직접 딕셔너리로 변환
        result = []
        for ann in announcements:
            result.append({
                "id": ann.id,
                "title": ann.title,
                "content": ann.content,
                "priority": ann.priority,
                "start_date": ann.start_date.isoformat() if ann.start_date else None,
                "end_date": ann.end_date.isoformat() if ann.end_date else None,
                "target_churches": ann.target_churches,
                "is_active": ann.is_active,
                "is_pinned": ann.is_pinned,
                "created_by": ann.created_by,
                "author_name": ann.author_name,
                "created_at": ann.created_at.isoformat() if ann.created_at else None,
                "updated_at": ann.updated_at.isoformat() if ann.updated_at else None
            })
        
        total = db.query(models.SystemAnnouncement).count()
        return {"announcements": result, "total": total}
        
    except Exception as e:
        print(f"Error in get_all_system_announcements_admin: {str(e)}")
        return {"error": str(e), "announcements": [], "total": 0}


@router.post("/", response_model=system_schemas.SystemAnnouncement)
def create_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    announcement_in: system_schemas.SystemAnnouncementCreate,
) -> Any:
    """
    시스템 공지사항 생성
    권한: church_id = 0인 사용자만
    """
    try:
        if current_user.church_id != 0:
            raise HTTPException(
                status_code=403,
                detail="시스템 관리자만 공지사항을 생성할 수 있습니다"
            )
        
        # 시스템 공지사항 생성
        announcement = models.SystemAnnouncement(
            **announcement_in.dict(),
            created_by=current_user.id,
            author_name=current_user.full_name or current_user.username
        )
        
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        
        return announcement
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_system_announcement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{announcement_id}", response_model=system_schemas.SystemAnnouncement)
def update_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    announcement_id: int,
    announcement_in: system_schemas.SystemAnnouncementUpdate,
) -> Any:
    """
    시스템 공지사항 수정
    권한: church_id = 0인 사용자만
    """
    try:
        if current_user.church_id != 0:
            raise HTTPException(
                status_code=403,
                detail="시스템 관리자만 공지사항을 수정할 수 있습니다"
            )
        
        announcement = db.query(models.SystemAnnouncement).filter(
            models.SystemAnnouncement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        # 업데이트
        update_data = announcement_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(announcement, field, value)
        
        announcement.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(announcement)
        
        return announcement
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_system_announcement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{announcement_id}")
def delete_system_announcement(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    announcement_id: int,
) -> Any:
    """
    시스템 공지사항 삭제
    권한: church_id = 0인 사용자만
    """
    try:
        if current_user.church_id != 0:
            raise HTTPException(
                status_code=403,
                detail="시스템 관리자만 공지사항을 삭제할 수 있습니다"
            )
        
        announcement = db.query(models.SystemAnnouncement).filter(
            models.SystemAnnouncement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        db.delete(announcement)
        db.commit()
        
        return {"success": True, "message": "공지사항이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in delete_system_announcement: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{announcement_id}/read")
def mark_system_announcement_as_read(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    announcement_id: int,
) -> Any:
    """
    시스템 공지사항 읽음 처리
    """
    try:
        # 시스템 공지사항 존재 확인
        announcement = db.query(models.SystemAnnouncement).filter(
            models.SystemAnnouncement.id == announcement_id
        ).first()
        
        if not announcement:
            raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없습니다")
        
        # 이미 읽음 처리되었는지 확인
        existing_read = db.query(models.SystemAnnouncementRead).filter(
            and_(
                models.SystemAnnouncementRead.system_announcement_id == announcement_id,
                models.SystemAnnouncementRead.user_id == current_user.id,
                models.SystemAnnouncementRead.church_id == current_user.church_id
            )
        ).first()
        
        if existing_read:
            return {"success": True, "message": "이미 읽음 처리되었습니다"}
        
        # 읽음 처리
        read_record = models.SystemAnnouncementRead(
            system_announcement_id=announcement_id,
            user_id=current_user.id,
            church_id=current_user.church_id
        )
        
        db.add(read_record)
        db.commit()
        
        return {"success": True, "message": "읽음 처리 완료"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in mark_system_announcement_as_read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/churches", response_model=List[dict])
def get_churches_for_targeting(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    공지사항 대상 설정을 위한 교회 목록 조회
    권한: church_id = 0인 사용자만
    """
    try:
        if current_user.church_id != 0:
            raise HTTPException(
                status_code=403,
                detail="시스템 관리자만 접근 가능합니다"
            )
        
        churches = db.query(models.Church).filter(
            models.Church.is_active == True
        ).all()
        
        result = []
        for church in churches:
            result.append({
                "id": church.id,
                "name": church.name,
                "address": getattr(church, 'address', ''),
                "phone": getattr(church, 'phone', '')
            })
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_churches_for_targeting: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")