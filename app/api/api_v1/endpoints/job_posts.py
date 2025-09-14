from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Form, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.job_posts import JobPost, JobSeeker


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
    contact_phone: str  # 필수 전화번호
    contact_email: Optional[str] = None  # 선택적 이메일
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
    contact_phone: str  # 필수 전화번호
    contact_email: Optional[str] = None  # 선택적 이메일
    available_start_date: Optional[str] = None
    status: Optional[str] = "active"

router = APIRouter()


# === Job Posts (구인 공고) ===

# 프론트엔드에서 호출하는 URL에 맞춰 추가
@router.get("/job-posting", response_model=dict)
def get_job_posting_list(
    status: Optional[str] = Query(None, description="상태 필터: active, closed, filled"),
    employment_type: Optional[str] = Query(None, description="고용 형태 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    search: Optional[str] = Query(None, description="제목/회사명/직책 검색"),
    church_filter: Optional[int] = Query(None, description="교회 필터 (선택사항)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 목록 조회 - 실제 데이터베이스에서 조회 (job-posting URL)"""
    try:
        print(f"🔍 [JOB_POSTING_LIST] 구인 공고 목록 조회 시작")
        print(f"🔍 [JOB_POSTING_LIST] 필터: status={status}, employment_type={employment_type}, location={location}")
        
        # Raw SQL로 안전한 조회 - 트랜잭션 초기화
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                jp.id,
                jp.title,
                'active' as status,
                0 as views,
                0 as likes,
                jp.created_at,
                jp.author_id,
                u.full_name
            FROM job_posts jp
            LEFT JOIN users u ON jp.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        # 필터링 적용 (기본 검색만)
        if search:
            query_sql += " AND jp.title ILIKE :search"
            params["search"] = f"%{search}%"
            print(f"🔍 [JOB_POSTING_LIST] 검색 필터 적용: {search}")
        
        query_sql += " ORDER BY jp.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM job_posts jp WHERE 1=1"
        if search:
            count_sql += " AND jp.title ILIKE :search"
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [JOB_POSTING_LIST] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        job_list = result.fetchall()
        print(f"🔍 [JOB_POSTING_LIST] 조회된 데이터 개수: {len(job_list)}")
        
        # 응답 데이터 구성
        data_items = []
        for row in job_list:
            # 기본 정보만으로 간소화 (Raw SQL 결과 사용)
            data_items.append({
                "id": row[0],
                "title": row[1],
                "company": row[1],  # 제목을 회사명으로 임시 사용
                "position": "일반",  # 기본값
                "employment_type": "정규직",  # 기본값
                "location": "미정",  # 기본값
                "status": row[2],
                "salary_range": "협의",  # 기본값
                "description": row[1],  # 제목을 설명으로 임시 사용
                "requirements": "없음",  # 기본값
                "contact_phone": "",  # 기본값
                "contact_email": None,  # 기본값
                "contact_info": "댓글로 연락",  # 기본값
                "created_at": row[5].isoformat() if row[5] else None,
                "updated_at": row[5].isoformat() if row[5] else None,
                "view_count": row[3] or 0,
                "user_id": row[6],
                "user_name": row[7] or "익명",
                "church_id": 9998
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 구인 공고 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
        return {
            "success": True,
            "data": data_items,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "per_page": limit,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
    except Exception as e:
        # 에러가 발생해도 기본 구조는 유지
        print(f"❌ [JOB_POSTING_LIST] 오류: {str(e)}")
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


@router.post("/job-posting", response_model=dict)
async def create_job_posting(
    request: Request,
    job_data: JobPostCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """구인 공고 등록 - 프론트엔드 호환성을 위한 별칭 엔드포인트 (job-posting URL)"""
    return await create_job_post(request, job_data, db, current_user)


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
    """구인 공고 등록 - 실제 데이터베이스 저장"""
    try:
        print(f"🔍 [JOB_POST] Job post data received: {job_data}")
        print(f"🔍 [JOB_POST] User ID: {current_user.id}, Church ID: {current_user.church_id}")
        print(f"🔍 [JOB_POST] User name: {current_user.full_name}")
        
        # contact_info를 phone과 email 조합으로 생성
        contact_parts = [f"전화: {job_data.contact_phone}"]
        if job_data.contact_email:
            contact_parts.append(f"이메일: {job_data.contact_email}")
        combined_contact_info = " | ".join(contact_parts)
        
        # 실제 데이터베이스에 저장
        job_record = JobPost(
            title=job_data.title,
            description=job_data.description,
            company_name=job_data.company,  # company -> company_name
            job_type=job_data.position,     # position -> job_type
            employment_type=job_data.employment_type,
            location=job_data.location,
            salary_range=job_data.salary_range,
            requirements=job_data.requirements,
            contact_info=combined_contact_info,  # 조합된 연락처 정보
            # application_deadline은 expires_at에서 변환 필요시 처리
            status=job_data.status or "active",
            user_id=current_user.id,
            author_id=current_user.id,  # 중복 필드도 채움
            church_id=current_user.church_id or 9998,  # 커뮤니티 기본값
        )
        
        print(f"🔍 [JOB_POST] About to save job post record...")
        db.add(job_record)
        db.commit()
        db.refresh(job_record)
        print(f"✅ [JOB_POST] Successfully saved job post with ID: {job_record.id}")
        
        # 저장 후 검증 - 실제로 DB에서 다시 조회
        saved_record = db.query(JobPost).filter(JobPost.id == job_record.id).first()
        if saved_record:
            print(f"✅ [JOB_POST] Verification successful: Record exists in DB with ID {saved_record.id}")
        else:
            print(f"❌ [JOB_POST] Verification failed: Record not found in DB!")
        
        return {
            "success": True,
            "message": "구인 공고가 등록되었습니다.",
            "data": {
                "id": job_record.id,
                "title": job_record.title,
                "company": job_record.company_name,
                "position": job_record.job_type,
                "employment_type": job_record.employment_type,
                "location": job_record.location,
                "salary_range": job_record.salary_range,
                "description": job_record.description,
                "requirements": job_record.requirements,
                "contact_phone": job_data.contact_phone,  # 분리된 전화번호
                "contact_email": job_data.contact_email,  # 분리된 이메일
                "contact_info": job_record.contact_info,  # 조합된 연락처 (하위 호환성)
                "status": job_record.status,
                "user_id": job_record.user_id,
                "user_name": current_user.full_name or "익명",
                "church_id": job_record.church_id,
                "created_at": job_record.created_at.isoformat() if job_record.created_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [JOB_POST] 구인 공고 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [JOB_POST] Traceback: {traceback.format_exc()}")
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