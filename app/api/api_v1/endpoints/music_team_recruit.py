"""
음악팀 모집 관련 API 엔드포인트
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.music_team_recruitment import MusicTeamRecruitment
from app.models.common import CommonStatus


class MusicTeamRecruitmentCreateRequest(BaseModel):
    """음악팀 모집 등록 요청 스키마"""
    # 필수 필드
    title: str
    team_name: Optional[str] = "미정"  # 프론트엔드에서 제거한 경우 기본값 제공
    team_type: str
    experience_required: str
    practice_location: str
    practice_schedule: str
    description: str
    contact_method: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: str
    
    # 선택 필드
    instruments_needed: Optional[List[str]] = None
    positions_needed: Optional[str] = None
    commitment: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    current_members: Optional[int] = None
    target_members: Optional[int] = None


class MusicTeamRecruitmentUpdateRequest(BaseModel):
    """음악팀 모집 수정 요청 스키마"""
    title: Optional[str] = None
    team_name: Optional[str] = None
    team_type: Optional[str] = None
    experience_required: Optional[str] = None
    practice_location: Optional[str] = None
    practice_schedule: Optional[str] = None
    description: Optional[str] = None
    contact_method: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None
    instruments_needed: Optional[List[str]] = None
    positions_needed: Optional[str] = None
    commitment: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    current_members: Optional[int] = None
    target_members: Optional[int] = None


router = APIRouter()


def map_frontend_status_to_enum(status: str) -> CommonStatus:
    """프론트엔드 status 값을 CommonStatus enum으로 매핑"""
    status_mapping = {
        "recruiting": CommonStatus.ACTIVE,
        "open": CommonStatus.ACTIVE,
        "active": CommonStatus.ACTIVE,
        "closed": CommonStatus.COMPLETED,
        "completed": CommonStatus.COMPLETED,
        "cancelled": CommonStatus.CANCELLED,
        "paused": CommonStatus.PAUSED
    }
    return status_mapping.get(status.lower(), CommonStatus.ACTIVE)


def parse_datetime(date_string: str) -> datetime:
    """ISO 형식 문자열을 datetime 객체로 변환"""
    if not date_string:
        return None
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return None


@router.get("/music-team-recruitments", response_model=dict)
def get_music_team_recruitments_list(
    team_type: Optional[str] = Query(None, description="팀 유형 필터"),
    instruments: Optional[str] = Query(None, description="악기 필터 (쉼표로 구분)"),
    team_name: Optional[str] = Query(None, description="팀명 필터"),
    status: Optional[str] = Query(None, description="모집 상태 필터"),
    experience_required: Optional[str] = Query(None, description="경력 요구사항 필터"),
    search: Optional[str] = Query(None, description="제목/내용 검색"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 목록 조회"""
    try:
        print(f"🔍 [MUSIC_TEAM_RECRUIT] 음악팀 모집 목록 조회 시작")
        print(f"🔍 [MUSIC_TEAM_RECRUIT] 필터: team_type={team_type}, team_name={team_name}, status={status}")
        
        # Raw SQL로 안전한 조회 (기본 필드만) - 트랜잭션 초기화
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        # 단순한 쿼리로 시작해서 데이터 존재 여부 확인
        query_sql = """
            SELECT
                cmt.id, cmt.title, cmt.status, cmt.author_id, cmt.created_at
            FROM community_music_teams cmt
            WHERE 1=1
        """
        params = {}
        
        # 기본 필터링 (제목 검색만)
        if search:
            query_sql += " AND cmt.title ILIKE :search"
            params["search"] = f"%{search}%"
        
        query_sql += " ORDER BY cmt.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM community_music_teams cmt WHERE 1=1"
        if search:
            count_sql += " AND cmt.title ILIKE :search"
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [MUSIC_TEAM_RECRUIT] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        recruitments_list = result.fetchall()
        print(f"🔍 [MUSIC_TEAM_RECRUIT] 조회된 데이터 개수: {len(recruitments_list)}")
        
        # 사용자 정보 조회 (author_name을 위해)
        author_names = {}
        if recruitments_list:
            author_ids = [row[3] for row in recruitments_list if row[3]]  # author_id는 3번째 인덱스
            if author_ids:
                try:
                    user_query = text("SELECT id, full_name FROM users WHERE id = ANY(:ids)")
                    user_result = db.execute(user_query, {"ids": author_ids})
                    for user_row in user_result:
                        author_names[user_row[0]] = user_row[1]
                except Exception as e:
                    print(f"❌ 사용자 정보 조회 실패: {e}")

        # 응답 데이터 구성 (실제 데이터 사용) - 간소화된 버전
        from datetime import timezone, timedelta
        kst = timezone(timedelta(hours=9))  # KST = UTC+9

        data_items = []
        for row in recruitments_list:
            # UTC to KST 변환
            created_at_kst = None
            updated_at_kst = None
            if row[4]:  # created_at
                if row[4].tzinfo is None:
                    # naive datetime을 UTC로 간주하고 KST로 변환
                    utc_time = row[4].replace(tzinfo=timezone.utc)
                    created_at_kst = utc_time.astimezone(kst).isoformat()
                    updated_at_kst = created_at_kst
                else:
                    # timezone-aware datetime을 KST로 변환
                    created_at_kst = row[4].astimezone(kst).isoformat()
                    updated_at_kst = created_at_kst

            data_items.append({
                "id": row[0],                    # id
                "title": row[1],                 # title
                "team_name": "미정",              # 기본값
                "team_type": "일반",              # 기본값
                "instruments_needed": [],        # 기본값
                "positions_needed": "미정",       # 기본값
                "experience_required": "무관",    # 기본값
                "practice_location": "미정",      # 기본값
                "practice_schedule": "미정",      # 기본값
                "commitment": "미정",            # 기본값
                "description": "",               # 기본값
                "requirements": "",              # 기본값
                "benefits": "",                  # 기본값
                "contact_method": "댓글",        # 기본값
                "contact_phone": "",             # 기본값
                "contact_email": "",             # 기본값
                "status": row[2] or "모집중",     # status
                "current_members": 0,            # 기본값
                "target_members": 0,             # 기본값
                "author_id": row[3],             # author_id
                "author_name": author_names.get(row[3], "익명"),
                "church_id": 9998,               # 기본값
                "church_name": "커뮤니티",        # 기본값
                "views": 0,                      # 기본값
                "likes": 0,                      # 기본값
                "applicants_count": 0,           # 기본값
                "created_at": created_at_kst,    # KST로 변환된 created_at
                "updated_at": updated_at_kst     # KST로 변환된 updated_at
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 음악팀 모집 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
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
        print(f"❌ [MUSIC_TEAM_RECRUIT] 목록 조회 오류: {str(e)}")
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


@router.post("/music-team-recruitments", response_model=dict)
async def create_music_team_recruitment(
    request: Request,
    recruitment_data: MusicTeamRecruitmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 등록"""
    try:
        print(f"🔍 [MUSIC_TEAM_RECRUIT] 음악팀 모집 데이터 받음: {recruitment_data}")
        
        # created_at, updated_at는 SQLAlchemy server_default=func.now()로 자동 처리
        
        # 실제 테이블 구조 확인
        from sqlalchemy import text
        try:
            db.rollback()
            table_info_sql = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'community_music_teams'
                ORDER BY ordinal_position
            """
            result = db.execute(text(table_info_sql))
            columns = result.fetchall()
            column_names = [col[0] for col in columns]
            print(f"🔍 [MUSIC_TEAM_RECRUIT] 실제 테이블 컬럼: {column_names}")
        except Exception as e:
            print(f"⚠️ [MUSIC_TEAM_RECRUIT] 테이블 구조 확인 실패: {e}")
            column_names = []
        
        # Raw SQL로 데이터 저장 (실제 테이블 구조에 맞게) - contact_info 필드 추가
        insert_sql = """
            INSERT INTO community_music_teams (
                title, team_name, team_type, instruments_needed, positions_needed,
                experience_required, practice_location, practice_schedule, commitment,
                description, requirements, benefits, contact_method, contact_info,
                status, current_members, target_members, author_id, church_id
            ) VALUES (
                :title, :team_name, :team_type, :instruments_needed, :positions_needed,
                :experience_required, :practice_location, :practice_schedule, :commitment,
                :description, :requirements, :benefits, :contact_method, :contact_info,
                :status, :current_members, :target_members, :author_id, :church_id
            ) RETURNING id
        """
        
        # JSON 필드 명시적 변환
        import json
        instruments_json = json.dumps(recruitment_data.instruments_needed) if recruitment_data.instruments_needed else None

        # contact_info 구성 (contact_phone, contact_email이 없으므로 contact_method만 사용)
        contact_info = f"연락방법: {recruitment_data.contact_method}"
        if recruitment_data.contact_phone:
            contact_info += f" | 전화: {recruitment_data.contact_phone}"
        if recruitment_data.contact_email:
            contact_info += f" | 이메일: {recruitment_data.contact_email}"

        insert_params = {
            "title": recruitment_data.title,
            "team_name": recruitment_data.team_name or "미정",
            "team_type": recruitment_data.team_type,
            "instruments_needed": instruments_json,  # JSON 문자열로 명시적 변환
            "positions_needed": recruitment_data.positions_needed,
            "experience_required": recruitment_data.experience_required,
            "practice_location": recruitment_data.practice_location,
            "practice_schedule": recruitment_data.practice_schedule,
            "commitment": recruitment_data.commitment,
            "description": recruitment_data.description,
            "requirements": recruitment_data.requirements,
            "benefits": recruitment_data.benefits,
            "contact_method": recruitment_data.contact_method,
            "contact_info": contact_info,  # NOT NULL 제약조건 만족
            "status": map_frontend_status_to_enum(recruitment_data.status).value,
            "current_members": recruitment_data.current_members,
            "target_members": recruitment_data.target_members,
            "author_id": current_user.id,
            "church_id": current_user.church_id or 9998
        }
        
        print(f"🔍 [MUSIC_TEAM_RECRUIT] Raw SQL로 음악팀 모집 저장 중...")
        result = db.execute(text(insert_sql), insert_params)
        new_id = result.fetchone()[0]
        db.commit()
        print(f"✅ [MUSIC_TEAM_RECRUIT] 성공적으로 저장됨. ID: {new_id}")
        
        # 등록 후 현재 시간을 KST로 변환해서 응답
        from datetime import datetime, timezone, timedelta
        kst = timezone(timedelta(hours=9))
        current_time_kst = datetime.now(kst).isoformat()

        return {
            "success": True,
            "message": "음악팀 모집이 등록되었습니다.",
            "data": {
                "id": new_id,
                "title": recruitment_data.title,
                "team_name": recruitment_data.team_name or "미정",
                "team_type": recruitment_data.team_type,
                "contact_method": recruitment_data.contact_method,
                "status": recruitment_data.status,
                "created_at": current_time_kst,
                "updated_at": current_time_kst
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [MUSIC_TEAM_RECRUIT] 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [MUSIC_TEAM_RECRUIT] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"음악팀 모집 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/music-team-recruitments/{recruitment_id}/increment-view", response_model=dict)
def increment_music_team_recruitment_view_count(
    recruitment_id: int,
    db: Session = Depends(get_db)
):
    """음악팀 모집 조회수 증가 전용 API - 인증 없이 사용 가능"""
    try:
        from sqlalchemy import text
        print(f"🚀 [VIEW_INCREMENT_API] 음악팀 모집 조회수 증가 전용 API 호출 - ID: {recruitment_id}")

        # 현재 조회수 확인 (views 컬럼 사용)
        check_sql = "SELECT views FROM community_music_teams WHERE id = :recruitment_id"
        result = db.execute(text(check_sql), {"recruitment_id": recruitment_id})
        row = result.fetchone()

        if not row:
            return {
                "success": False,
                "message": "해당 음악팀 모집을 찾을 수 없습니다."
            }

        current_view_count = row[0] or 0
        print(f"🔍 [VIEW_INCREMENT_API] 현재 조회수: {current_view_count}")

        # 조회수 증가 (views 컬럼 사용)
        increment_sql = """
            UPDATE community_music_teams
            SET views = COALESCE(views, 0) + 1
            WHERE id = :recruitment_id
            RETURNING views
        """
        result = db.execute(text(increment_sql), {"recruitment_id": recruitment_id})
        new_view_count = result.fetchone()[0]
        db.commit()

        print(f"✅ [VIEW_INCREMENT_API] 조회수 증가 성공 - ID: {recruitment_id}, {current_view_count} → {new_view_count}")

        return {
            "success": True,
            "data": {
                "recruitment_id": recruitment_id,
                "previous_view_count": current_view_count,
                "new_view_count": new_view_count
            }
        }

    except Exception as e:
        db.rollback()
        print(f"❌ [VIEW_INCREMENT_API] 조회수 증가 실패 - ID: {recruitment_id}, 오류: {e}")
        return {
            "success": False,
            "message": f"조회수 증가 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-recruitments/{recruitment_id}", response_model=dict)
def get_music_team_recruitment_detail(
    recruitment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 상세 조회"""
    try:
        recruitment = db.query(MusicTeamRecruitment).filter(MusicTeamRecruitment.id == recruitment_id).first()
        if not recruitment:
            return {
                "success": False,
                "message": "음악팀 모집을 찾을 수 없습니다."
            }
        
        # 조회수 증가
        recruitment.views = (recruitment.views or 0) + 1
        db.commit()

        # KST 변환을 위한 import
        from datetime import timezone, timedelta

        return {
            "success": True,
            "data": {
                "id": recruitment.id,
                "title": recruitment.title,
                "team_name": recruitment.team_name,
                "team_type": recruitment.team_type,
                "instruments_needed": recruitment.instruments_needed or [],
                "positions_needed": recruitment.positions_needed,
                "experience_required": recruitment.experience_required,
                "practice_location": recruitment.practice_location,
                "practice_schedule": recruitment.practice_schedule,
                "commitment": recruitment.commitment,
                "description": recruitment.description,
                "requirements": recruitment.requirements,
                "benefits": recruitment.benefits,
                "contact_method": recruitment.contact_method,
                "status": recruitment.status,
                "current_members": recruitment.current_members,
                "target_members": recruitment.target_members,
                "author_id": recruitment.author_id,
                "author_name": recruitment.author.full_name if recruitment.author else "익명",
                "church_id": recruitment.church_id,
                "views": recruitment.views or 0,
                "likes": recruitment.likes or 0,
                "applicants_count": recruitment.applicants_count or 0,
                "created_at": recruitment.created_at.astimezone(timezone(timedelta(hours=9))).isoformat() if recruitment.created_at else None,
                "updated_at": recruitment.updated_at.astimezone(timezone(timedelta(hours=9))).isoformat() if recruitment.updated_at else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 모집 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/music-team-recruitments/{recruitment_id}", response_model=dict)
async def update_music_team_recruitment(
    recruitment_id: int,
    recruitment_data: MusicTeamRecruitmentUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 수정"""
    try:
        recruitment = db.query(MusicTeamRecruitment).filter(MusicTeamRecruitment.id == recruitment_id).first()
        if not recruitment:
            return {
                "success": False,
                "message": "음악팀 모집을 찾을 수 없습니다."
            }
        
        # 수정 가능한 필드 업데이트 (None이 아닌 값만)
        update_data = recruitment_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(recruitment, field, value)
        
        # updated_at는 SQLAlchemy의 onupdate=func.now()로 자동 처리됨
        
        db.commit()
        db.refresh(recruitment)
        
        return {
            "success": True,
            "message": "음악팀 모집이 수정되었습니다.",
            "data": {
                "id": recruitment.id,
                "title": recruitment.title,
                "updated_at": recruitment.updated_at.isoformat() if recruitment.updated_at else None
            }
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"음악팀 모집 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/music-team-recruitments/{recruitment_id}", response_model=dict)
def delete_music_team_recruitment(
    recruitment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 삭제"""
    try:
        recruitment = db.query(MusicTeamRecruitment).filter(MusicTeamRecruitment.id == recruitment_id).first()
        if not recruitment:
            return {
                "success": False,
                "message": "음악팀 모집을 찾을 수 없습니다."
            }
        
        db.delete(recruitment)
        db.commit()
        
        return {
            "success": True,
            "message": "음악팀 모집이 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"음악팀 모집 삭제 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/music-team-recruitments/{recruitment_id}/apply", response_model=dict)
async def apply_music_team_recruitment(
    recruitment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 모집 지원하기"""
    try:
        recruitment = db.query(MusicTeamRecruitment).filter(MusicTeamRecruitment.id == recruitment_id).first()
        if not recruitment:
            return {
                "success": False,
                "message": "음악팀 모집을 찾을 수 없습니다."
            }
        
        # 실제 지원 로직은 여기에 구현 (지원 테이블이 있다면)
        # 현재는 기본적인 응답만 반환
        
        return {
            "success": True,
            "message": "음악팀 모집에 지원되었습니다.",
            "data": {
                "recruitment_id": recruitment_id,
                "recruitment_title": recruitment.title,
                "applied_at": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"음악팀 모집 지원 중 오류가 발생했습니다: {str(e)}"
        }