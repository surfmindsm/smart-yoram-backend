from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.job_post import JobPost, JobSeeker
from app.schemas.job_schemas import JobPost as JobSchemas, JobSeeker as SeekerSchemas

router = APIRouter()


# === Job Posts (구인 공고) ===

@router.get("/job-posts", response_model=dict)
def get_job_posts(
    status: Optional[str] = Query(None, description="상태 필터: open, closed, filled"),
    employment_type: Optional[str] = Query(None, description="고용 형태 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/회사명/직책 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 목록 조회"""
    try:
        query = db.query(JobPost)
        
        if church_filter:
            query = query.filter(JobPost.church_id == church_filter)
        
        if status:
            query = query.filter(JobPost.status == status)
        
        if employment_type:
            query = query.filter(JobPost.employment_type == employment_type)
        
        if location:
            query = query.filter(JobPost.location.contains(location))
        
        if search:
            search_filter = or_(
                JobPost.title.contains(search),
                JobPost.company.contains(search),
                JobPost.position.contains(search)
            )
            query = query.filter(search_filter)
        
        total_count = query.count()
        skip = (page - 1) * limit
        job_posts = query.order_by(desc(JobPost.created_at)).offset(skip).limit(limit).all()
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": [JobSchemas.Response.from_orm(post) for post in job_posts],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"구인 공고 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/job-posts", response_model=dict)
async def create_job_post(
    title: str = Form(..., description="제목"),
    company: str = Form(..., description="회사명"),
    position: str = Form(..., description="직책/포지션"),
    employment_type: str = Form(..., description="고용 형태"),
    location: str = Form(..., description="근무 지역"),
    salary: Optional[str] = Form(None, description="급여"),
    work_hours: Optional[str] = Form(None, description="근무 시간"),
    description: str = Form(..., description="상세 설명"),
    requirements: Optional[str] = Form(None, description="자격 요건"),
    benefits: Optional[str] = Form(None, description="복리후생"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    deadline: Optional[str] = Form(None, description="마감일 (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 등록"""
    try:
        church_id = 9998 if current_user.church_id == 9998 else current_user.church_id
        
        job_data = {
            "title": title,
            "company": company,
            "position": position,
            "employment_type": employment_type,
            "location": location,
            "salary": salary,
            "work_hours": work_hours,
            "description": description,
            "requirements": requirements,
            "benefits": benefits,
            "contact_method": contact_method,
            "contact_info": contact_info,
            "author_id": current_user.id,
            "church_id": church_id,
            "status": "open"
        }
        
        if deadline:
            try:
                job_data["deadline"] = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            except:
                pass
        
        db_job = JobPost(**job_data)
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        
        return {
            "success": True,
            "message": "구인 공고가 등록되었습니다.",
            "data": JobSchemas.Response.from_orm(db_job)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"구인 공고 등록 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/job-posts/{job_id}", response_model=dict)
def get_job_post_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 상세 조회"""
    try:
        job_post = db.query(JobPost).filter(JobPost.id == job_id).first()
        
        if not job_post:
            raise HTTPException(status_code=404, detail="해당 구인 공고를 찾을 수 없습니다.")
        
        job_post.views += 1
        db.commit()
        
        return {
            "success": True,
            "data": JobSchemas.Response.from_orm(job_post)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"구인 공고 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/job-posts/{job_id}", response_model=dict)
def update_job_post(
    job_id: int,
    updates: JobSchemas.Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 수정"""
    try:
        job_post = db.query(JobPost).filter(JobPost.id == job_id).first()
        
        if not job_post:
            raise HTTPException(status_code=404, detail="해당 구인 공고를 찾을 수 없습니다.")
        
        if job_post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="본인이 작성한 공고만 수정할 수 있습니다.")
        
        update_data = updates.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(job_post, field, value)
        
        db.commit()
        db.refresh(job_post)
        
        return {
            "success": True,
            "message": "구인 공고가 수정되었습니다.",
            "data": JobSchemas.Response.from_orm(job_post)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"구인 공고 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/job-posts/{job_id}", response_model=dict)
def delete_job_post(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 삭제"""
    try:
        job_post = db.query(JobPost).filter(JobPost.id == job_id).first()
        
        if not job_post:
            raise HTTPException(status_code=404, detail="해당 구인 공고를 찾을 수 없습니다.")
        
        if job_post.author_id != current_user.id and current_user.church_id != 0:
            raise HTTPException(status_code=403, detail="본인이 작성한 공고만 삭제할 수 있습니다.")
        
        db.delete(job_post)
        db.commit()
        
        return {
            "success": True,
            "message": "구인 공고가 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"구인 공고 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# === Job Seekers (구직 신청) ===

@router.get("/job-seekers", response_model=dict)
def get_job_seekers(
    status: Optional[str] = Query(None, description="상태 필터: active, inactive"),
    employment_type: Optional[str] = Query(None, description="희망 고용 형태 필터"),
    desired_location: Optional[str] = Query(None, description="희망 지역 필터"),
    search: Optional[str] = Query(None, description="제목/희망직책 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 목록 조회"""
    try:
        query = db.query(JobSeeker)
        
        if church_filter:
            query = query.filter(JobSeeker.church_id == church_filter)
        
        if status:
            query = query.filter(JobSeeker.status == status)
        
        if employment_type:
            query = query.filter(JobSeeker.employment_type == employment_type)
        
        if desired_location:
            query = query.filter(JobSeeker.desired_location.contains(desired_location))
        
        if search:
            search_filter = or_(
                JobSeeker.title.contains(search),
                JobSeeker.desired_position.contains(search)
            )
            query = query.filter(search_filter)
        
        total_count = query.count()
        skip = (page - 1) * limit
        job_seekers = query.order_by(desc(JobSeeker.created_at)).offset(skip).limit(limit).all()
        
        total_pages = (total_count + limit - 1) // limit
        
        return {
            "success": True,
            "data": [SeekerSchemas.Response.from_orm(seeker) for seeker in job_seekers],
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"구직 신청 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/job-seekers", response_model=dict)
async def create_job_seeker(
    title: str = Form(..., description="제목"),
    desired_position: str = Form(..., description="희망 직책"),
    employment_type: str = Form(..., description="희망 고용 형태"),
    desired_location: str = Form(..., description="희망 근무 지역"),
    desired_salary: Optional[str] = Form(None, description="희망 급여"),
    experience: Optional[str] = Form(None, description="경력"),
    skills: Optional[str] = Form(None, description="기술/스킬"),
    education: Optional[str] = Form(None, description="학력"),
    introduction: str = Form(..., description="자기소개"),
    contact_method: str = Form(..., description="연락 방법"),
    contact_info: str = Form(..., description="연락처"),
    available_from: Optional[str] = Form(None, description="근무 가능 시작일 (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 등록"""
    try:
        church_id = 9998 if current_user.church_id == 9998 else current_user.church_id
        
        seeker_data = {
            "title": title,
            "desired_position": desired_position,
            "employment_type": employment_type,
            "desired_location": desired_location,
            "desired_salary": desired_salary,
            "experience": experience,
            "skills": skills,
            "education": education,
            "introduction": introduction,
            "contact_method": contact_method,
            "contact_info": contact_info,
            "author_id": current_user.id,
            "church_id": church_id,
            "status": "active"
        }
        
        if available_from:
            try:
                seeker_data["available_from"] = datetime.fromisoformat(available_from.replace('Z', '+00:00'))
            except:
                pass
        
        db_seeker = JobSeeker(**seeker_data)
        db.add(db_seeker)
        db.commit()
        db.refresh(db_seeker)
        
        return {
            "success": True,
            "message": "구직 신청이 등록되었습니다.",
            "data": SeekerSchemas.Response.from_orm(db_seeker)
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"구직 신청 등록 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/job-seekers/{seeker_id}", response_model=dict)
def get_job_seeker_detail(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 상세 조회"""
    try:
        job_seeker = db.query(JobSeeker).filter(JobSeeker.id == seeker_id).first()
        
        if not job_seeker:
            raise HTTPException(status_code=404, detail="해당 구직 신청을 찾을 수 없습니다.")
        
        job_seeker.views += 1
        db.commit()
        
        return {
            "success": True,
            "data": SeekerSchemas.Response.from_orm(job_seeker)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"구직 신청 상세 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/job-seekers/{seeker_id}", response_model=dict)
def delete_job_seeker(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 삭제"""
    try:
        job_seeker = db.query(JobSeeker).filter(JobSeeker.id == seeker_id).first()
        
        if not job_seeker:
            raise HTTPException(status_code=404, detail="해당 구직 신청을 찾을 수 없습니다.")
        
        if job_seeker.author_id != current_user.id and current_user.church_id != 0:
            raise HTTPException(status_code=403, detail="본인이 작성한 신청만 삭제할 수 있습니다.")
        
        db.delete(job_seeker)
        db.commit()
        
        return {
            "success": True,
            "message": "구직 신청이 삭제되었습니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"구직 신청 삭제 중 오류가 발생했습니다: {str(e)}"
        )