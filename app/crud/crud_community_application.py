from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.community_application import CommunityApplication
from app.schemas.community_application import (
    CommunityApplicationCreate,
    CommunityApplicationUpdate,
    CommunityApplicationApprove,
    CommunityApplicationReject,
)


class CRUDCommunityApplication(CRUDBase[CommunityApplication, CommunityApplicationCreate, CommunityApplicationUpdate]):
    def create_application(
        self, db: Session, *, obj_in: CommunityApplicationCreate
    ) -> CommunityApplication:
        """신청서 생성"""
        obj_in_data = obj_in.dict()
        db_obj = CommunityApplication(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(
        self, db: Session, *, email: str
    ) -> Optional[CommunityApplication]:
        """이메일로 신청서 조회"""
        return db.query(CommunityApplication).filter(CommunityApplication.email == email).first()

    def get_applications_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        applicant_type: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "submitted_at",
        sort_order: str = "desc"
    ) -> tuple[List[CommunityApplication], int]:
        """필터링과 검색을 포함한 신청서 목록 조회"""
        query = db.query(CommunityApplication)
        
        # 상태 필터
        if status and status != "all":
            query = query.filter(CommunityApplication.status == status)
        
        # 신청자 유형 필터
        if applicant_type and applicant_type != "all":
            query = query.filter(CommunityApplication.applicant_type == applicant_type)
        
        # 검색 (조직명, 담당자명, 이메일)
        if search:
            search_filter = or_(
                CommunityApplication.organization_name.contains(search),
                CommunityApplication.contact_person.contains(search),
                CommunityApplication.email.contains(search)
            )
            query = query.filter(search_filter)
        
        # 정렬
        sort_column = getattr(CommunityApplication, sort_by, CommunityApplication.submitted_at)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # 전체 개수
        total_count = query.count()
        
        # 페이징
        applications = query.offset(skip).limit(limit).all()
        
        return applications, total_count

    def get_statistics(self, db: Session) -> Dict[str, int]:
        """신청서 상태별 통계"""
        stats = {
            "pending": db.query(CommunityApplication).filter(CommunityApplication.status == "pending").count(),
            "approved": db.query(CommunityApplication).filter(CommunityApplication.status == "approved").count(),
            "rejected": db.query(CommunityApplication).filter(CommunityApplication.status == "rejected").count(),
        }
        stats["total"] = sum(stats.values())
        return stats

    def approve_application(
        self,
        db: Session,
        *,
        application_id: int,
        reviewed_by: int,
        notes: Optional[str] = None
    ) -> Optional[CommunityApplication]:
        """신청서 승인"""
        application = db.query(CommunityApplication).filter(CommunityApplication.id == application_id).first()
        if not application:
            return None
        
        application.status = "approved"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = reviewed_by
        if notes:
            application.notes = notes
        
        db.commit()
        db.refresh(application)
        return application

    def reject_application(
        self,
        db: Session,
        *,
        application_id: int,
        reviewed_by: int,
        rejection_reason: str,
        notes: Optional[str] = None
    ) -> Optional[CommunityApplication]:
        """신청서 반려"""
        application = db.query(CommunityApplication).filter(CommunityApplication.id == application_id).first()
        if not application:
            return None
        
        application.status = "rejected"
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by = reviewed_by
        application.rejection_reason = rejection_reason
        if notes:
            application.notes = notes
        
        db.commit()
        db.refresh(application)
        return application

    def get_with_reviewer(self, db: Session, *, application_id: int) -> Optional[CommunityApplication]:
        """검토자 정보를 포함한 신청서 조회"""
        from app.models.user import User
        return (
            db.query(CommunityApplication)
            .outerjoin(User, CommunityApplication.reviewed_by == User.id)
            .filter(CommunityApplication.id == application_id)
            .first()
        )


community_application = CRUDCommunityApplication(CommunityApplication)