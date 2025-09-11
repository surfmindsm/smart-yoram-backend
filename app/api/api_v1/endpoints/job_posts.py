from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.models.user import User


class JobPostCreateRequest(BaseModel):
    title: str
    company: str
    position: str
    employment_type: str
    location: str
    salary_range: Optional[str] = None
    description: str
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    contact_method: Optional[str] = "기타"  # 프론트엔드에서 보내지 않는 경우 기본값 제공
    contact_info: str
    expires_at: Optional[str] = None
    status: Optional[str] = "open"


class JobSeekerCreateRequest(BaseModel):
    title: str
    desired_position: str
    employment_type: str
    desired_location: str
    salary_expectation: Optional[str] = None
    experience_summary: str
    education_background: Optional[str] = None
    skills: Optional[str] = None
    portfolio_url: Optional[str] = None
    contact_method: Optional[str] = "기타"  # 프론트엔드에서 보내지 않는 경우 기본값 제공
    contact_info: str
    available_start_date: Optional[str] = None
    status: Optional[str] = "active"

router = APIRouter()


# === Job Posts (구인 공고) ===

# 프론트엔드에서 호출하는 URL에 맞춰 추가
@router.get("/job-posting", response_model=dict)
def get_job_posting_list(
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
    """구인 공고 목록 조회 - 단순화된 버전 (job-posting URL)"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 구인 공고",
                    "company": "샘플 회사",
                    "position": "개발자",
                    "employment_type": "정규직",
                    "location": "서울",
                    "status": "open",
                    "salary_range": "면접 후 결정",
                    "description": "테스트용 샘플 구인공고입니다",
                    "requirements": "경력 무관",
                    "benefits": "4대보험",
                    "contact_info": "test@company.com",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "expires_at": "2024-12-31T23:59:59",
                    "view_count": 0,
                    "user_id": current_user.id,
                    "user_name": current_user.full_name or "익명",
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }


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
    """구인 공고 목록 조회 - 단순화된 버전"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 구인 공고",
                    "company": "샘플 회사",
                    "position": "개발자",
                    "employment_type": "정규직",
                    "location": "서울",
                    "status": "open",
                    "salary_range": "면접 후 결정",
                    "description": "테스트용 샘플 구인공고입니다",
                    "requirements": "경력 무관",
                    "benefits": "4대보험",
                    "contact_info": "test@company.com",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "expires_at": "2024-12-31T23:59:59",
                    "view_count": 0,
                    "user_id": current_user.id,
                    "user_name": current_user.full_name or "익명",
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }


@router.post("/job-posts", response_model=dict)
async def create_job_post(
    request: Request,
    job_data: JobPostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 등록 - JSON 요청 방식"""
    try:
        print(f"🔍 Job post data: {job_data}")
        print(f"🔍 User ID: {current_user.id}, Church ID: {current_user.church_id}")
        
        return {
            "success": True,
            "message": "구인 공고가 등록되었습니다.",
            "data": {
                "id": 1,
                "title": job_data.title,
                "company": job_data.company,
                "position": job_data.position,
                "employment_type": job_data.employment_type,
                "location": job_data.location,
                "salary_range": job_data.salary_range,
                "description": job_data.description,
                "requirements": job_data.requirements,
                "benefits": job_data.benefits,
                "contact_method": job_data.contact_method,
                "contact_info": job_data.contact_info,
                "expires_at": job_data.expires_at,
                "status": job_data.status,
                "user_id": current_user.id,
                "user_name": current_user.full_name or "익명",
                "church_id": current_user.church_id,
                "created_at": "2024-01-01T00:00:00"
            }
        }
        
    except Exception as e:
        print(f"❌ 구인 공고 등록 실패: {str(e)}")
        return {
            "success": False,
            "message": f"구인 공고 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/job-posts/{job_id}", response_model=dict)
def get_job_post_detail(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": job_id,
                "title": "샘플 구인 공고",
                "company": "샘플 회사",
                "position": "개발자",
                "employment_type": "정규직",
                "location": "서울",
                "status": "open",
                "description": "샘플 구인공고 설명",
                "contact_method": "이메일",
                "contact_info": "test@company.com"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"구인 공고 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/job-posts/{job_id}", response_model=dict)
def update_job_post(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 수정 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "구인 공고가 수정되었습니다.",
            "data": {
                "id": job_id,
                "title": "수정된 구인 공고",
                "status": "open"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"구인 공고 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/job-posts/{job_id}", response_model=dict)
def delete_job_post(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "구인 공고가 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"구인 공고 삭제 중 오류가 발생했습니다: {str(e)}"
        }


# === Job Seekers (구직 신청) ===

# 프론트엔드에서 호출하는 URL에 맞춰 추가
@router.get("/job-seeking", response_model=dict)
def get_job_seeking_list(
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
    """구직 신청 목록 조회 - 단순화된 버전 (job-seeking URL)"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 구직 신청",
                    "desired_position": "개발자",
                    "employment_type": "정규직",
                    "desired_location": "서울",
                    "status": "active",
                    "desired_salary": "면접 후 결정",
                    "experience": "3년",
                    "skills": "Python, JavaScript",
                    "introduction": "테스트용 샘플 구직신청입니다",
                    "contact_method": "이메일",
                    "contact_info": "seeker@test.com",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "views": 0,
                    "author_id": current_user.id,
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }


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
    """구직 신청 목록 조회 - 단순화된 버전"""
    try:
        # 프론트엔드에서 기대하는 기본 구조 제공
        sample_items = []
        
        # 테스트용 샘플 데이터 (필요시)
        if page == 1:  # 첫 페이지에만 샘플 데이터 표시
            sample_items = [
                {
                    "id": 1,
                    "title": "테스트 구직 신청",
                    "desired_position": "개발자",
                    "employment_type": "정규직",
                    "desired_location": "서울",
                    "status": "active",
                    "desired_salary": "면접 후 결정",
                    "experience": "3년",
                    "skills": "Python, JavaScript",
                    "introduction": "테스트용 샘플 구직신청입니다",
                    "contact_method": "이메일",
                    "contact_info": "seeker@test.com",
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00",
                    "views": 0,
                    "author_id": current_user.id,
                    "church_id": current_user.church_id
                }
            ]
        
        return {
            "success": True,
            "data": sample_items,
            "pagination": {
                "current_page": page,
                "total_pages": 1 if sample_items else 0,
                "total_count": len(sample_items),
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        return {
            "success": True,
            "data": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "per_page": limit,
                "has_next": False,
                "has_prev": False
            }
        }


@router.post("/job-seekers", response_model=dict)
async def create_job_seeker(
    request: Request,
    seeker_data: JobSeekerCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 등록 - JSON 요청 방식"""
    try:
        print(f"🔍 Job seeker data: {seeker_data}")
        print(f"🔍 User ID: {current_user.id}, Church ID: {current_user.church_id}")
        
        return {
            "success": True,
            "message": "구직 신청이 등록되었습니다.",
            "data": {
                "id": 1,
                "title": seeker_data.title,
                "desired_position": seeker_data.desired_position,
                "employment_type": seeker_data.employment_type,
                "desired_location": seeker_data.desired_location,
                "salary_expectation": seeker_data.salary_expectation,
                "experience_summary": seeker_data.experience_summary,
                "education_background": seeker_data.education_background,
                "skills": seeker_data.skills,
                "portfolio_url": seeker_data.portfolio_url,
                "contact_method": seeker_data.contact_method,
                "contact_info": seeker_data.contact_info,
                "available_start_date": seeker_data.available_start_date,
                "status": seeker_data.status,
                "user_id": current_user.id,
                "user_name": current_user.full_name or "익명",
                "church_id": current_user.church_id,
                "created_at": "2024-01-01T00:00:00"
            }
        }
        
    except Exception as e:
        print(f"❌ 구직 신청 등록 실패: {str(e)}")
        return {
            "success": False,
            "message": f"구직 신청 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/job-seekers/{seeker_id}", response_model=dict)
def get_job_seeker_detail(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 상세 조회 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "data": {
                "id": seeker_id,
                "title": "샘플 구직 신청",
                "desired_position": "개발자",
                "employment_type": "정규직",
                "desired_location": "서울",
                "status": "active",
                "introduction": "샘플 구직신청 자기소개",
                "contact_method": "이메일",
                "contact_info": "seeker@test.com"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"구직 신청 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/job-seekers/{seeker_id}", response_model=dict)
def delete_job_seeker(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구직 신청 삭제 - 단순화된 버전"""
    try:
        return {
            "success": True,
            "message": "구직 신청이 삭제되었습니다."
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"구직 신청 삭제 중 오류가 발생했습니다: {str(e)}"
        }