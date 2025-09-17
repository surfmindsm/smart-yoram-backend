"""
음악팀 지원자(Music Team Seekers) 관련 API 엔드포인트
연주자/팀이 교회 행사에 지원하는 시스템
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.music_team_seeker import MusicTeamSeeker
from app.models.common import CommonStatus


class MusicTeamSeekerCreateRequest(BaseModel):
    """음악팀 지원서 등록 요청 스키마"""
    # 필수 필드
    title: str
    instrument: str
    contact_phone: str
    
    # 선택 필드
    team_name: Optional[str] = None
    experience: Optional[str] = None
    portfolio: Optional[str] = None
    preferred_location: Optional[List[str]] = None
    available_days: Optional[List[str]] = None
    available_time: Optional[str] = None
    contact_email: Optional[str] = None


class MusicTeamSeekerUpdateRequest(BaseModel):
    """음악팀 지원서 수정 요청 스키마"""
    title: Optional[str] = None
    team_name: Optional[str] = None
    instrument: Optional[str] = None
    experience: Optional[str] = None
    portfolio: Optional[str] = None
    preferred_location: Optional[List[str]] = None
    available_days: Optional[List[str]] = None
    available_time: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    status: Optional[str] = None


router = APIRouter()


def map_frontend_status_to_enum(status: str) -> CommonStatus:
    """프론트엔드 status 값을 CommonStatus enum으로 매핑"""
    status_mapping = {
        "available": CommonStatus.ACTIVE,
        "active": CommonStatus.ACTIVE,
        "recruiting": CommonStatus.ACTIVE,
        "matched": CommonStatus.COMPLETED,
        "completed": CommonStatus.COMPLETED,
        "cancelled": CommonStatus.CANCELLED,
        "paused": CommonStatus.PAUSED
    }
    return status_mapping.get(status.lower(), CommonStatus.ACTIVE)


@router.get("/music-team-seekers", response_model=dict)
def get_music_team_seekers_list(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    status: Optional[str] = Query(None, description="상태 필터"),
    instrument: Optional[str] = Query(None, description="팀 형태 필터"),
    location: Optional[str] = Query(None, description="지역 필터"),
    day: Optional[str] = Query(None, description="요일 필터"),
    time: Optional[str] = Query(None, description="시간대 필터"),
    search: Optional[str] = Query(None, description="제목/경력 검색"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 목록 조회"""
    try:
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 지원서 목록 조회 시작")
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 필터: status={status}, instrument={instrument}, location={location}")
        
        # Raw SQL로 안전한 조회 - 트랜잭션 초기화
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                mts.id, mts.title, mts.team_name, mts.instrument, mts.experience,
                mts.portfolio, mts.preferred_location, mts.available_days,
                mts.available_time, mts.contact_phone, mts.contact_email,
                mts.status, mts.author_id, mts.church_id, mts.church_name,
                mts.view_count, mts.likes, mts.matches, mts.applications,
                mts.created_at, mts.updated_at, u.full_name
            FROM music_team_seekers mts
            LEFT JOIN users u ON mts.author_id = u.id
            WHERE 1=1
        """
        params = {}
        
        # 기본 필터링 (검색만)
        if search:
            query_sql += " AND mts.title ILIKE :search"
            params["search"] = f"%{search}%"
            print(f"🔍 [MUSIC_TEAM_SEEKERS] 검색 필터 적용: {search}")
        
        query_sql += " ORDER BY mts.created_at DESC"
        
        # 전체 개수 계산
        count_sql = "SELECT COUNT(*) FROM music_team_seekers mts WHERE 1=1"
        if search:
            count_sql += " AND mts.title ILIKE :search"
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar() or 0
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 필터링 후 전체 데이터 개수: {total_count}")
        
        # 페이지네이션
        offset = (page - 1) * limit
        query_sql += f" OFFSET {offset} LIMIT {limit}"
        
        result = db.execute(text(query_sql), params)
        seekers_list = result.fetchall()
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 조회된 데이터 개수: {len(seekers_list)}")
        
        # 응답 데이터 구성 (실제 조회된 데이터 사용)
        data_items = []
        for row in seekers_list:
            # 배열 필드 처리 (PostgreSQL 배열을 Python 리스트로 변환)
            preferred_location = row[6] if row[6] else []
            available_days = row[7] if row[7] else []
            
            data_items.append({
                "id": row[0],                              # id
                "title": row[1],                           # title
                "team_name": row[2] or "",                 # team_name (실제 데이터)
                "instrument": row[3] or "",                # instrument (실제 데이터)
                "experience": row[4] or "",                # experience (실제 데이터)
                "portfolio": row[5] or "",                 # portfolio (실제 데이터)
                "preferred_location": preferred_location,   # preferred_location (실제 데이터)
                "available_days": available_days,          # available_days (실제 데이터)
                "available_time": row[8] or "",            # available_time (실제 데이터)
                "contact_phone": row[9] or "",             # contact_phone (실제 데이터)
                "contact_email": row[10] or "",            # contact_email (실제 데이터)
                "status": row[11] or "available",          # status (실제 데이터)
                "author_id": row[12],                      # author_id
                "author_name": row[21] or "익명",          # full_name from users table
                "church_id": row[13] or 9998,              # church_id (실제 데이터)
                "church_name": row[14] or "커뮤니티",       # church_name (실제 데이터)
                "views": row[15] or 0,                     # view_count (실제 데이터)
                "view_count": row[15] or 0,                # 프론트엔드 호환성을 위한 view_count 필드
                "likes": row[16] or 0,                     # likes (실제 데이터)
                "matches": row[17] or 0,                   # matches (실제 데이터)
                "applications": row[18] or 0,              # applications (실제 데이터)
                "created_at": row[19].isoformat() if row[19] else None,  # created_at
                "updated_at": row[20].isoformat() if row[20] else None   # updated_at
            })
        
        total_pages = (total_count + limit - 1) // limit
        
        print(f"🔍 음악팀 지원서 목록 조회: 총 {total_count}개, 페이지 {page}/{total_pages}")
        
        return {
            "success": True,
            "data": {
                "items": data_items,
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total_count,
                    "pages": total_pages
                }
            }
        }
        
    except Exception as e:
        print(f"❌ [MUSIC_TEAM_SEEKERS] 목록 조회 오류: {str(e)}")
        return {
            "success": True,
            "data": {
                "items": [],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": 0,
                    "pages": 0
                }
            }
        }


@router.post("/music-team-seekers", response_model=dict)
async def create_music_team_seeker(
    request: Request,
    seeker_data: dict,  # dict로 받아서 JSON 문자열 파싱 처리
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 등록"""
    try:
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 지원서 데이터 받음: {seeker_data}")
        
        # JSON 문자열을 배열로 파싱
        import json
        
        # preferred_location 파싱
        preferred_location = []
        if seeker_data.get('preferred_location'):
            try:
                if isinstance(seeker_data['preferred_location'], str):
                    preferred_location = json.loads(seeker_data['preferred_location'])
                else:
                    preferred_location = seeker_data['preferred_location']
            except:
                preferred_location = []
        
        # available_days 파싱
        available_days = []
        if seeker_data.get('available_days'):
            try:
                if isinstance(seeker_data['available_days'], str):
                    available_days = json.loads(seeker_data['available_days'])
                else:
                    available_days = seeker_data['available_days']
            except:
                available_days = []
        
        print(f"🔍 [MUSIC_TEAM_SEEKERS] 파싱된 데이터: preferred_location={preferred_location}, available_days={available_days}")
        
        # created_at, updated_at는 SQLAlchemy server_default=func.now()로 자동 처리
        
        # Raw SQL로 데이터 저장 (실제 테이블 구조에 맞게) - 컬럼명 불일치 해결
        from sqlalchemy import text
        
        # 실제 테이블 구조 확인
        try:
            db.rollback()
            table_info_sql = """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'music_team_seekers'
                ORDER BY ordinal_position
            """
            result = db.execute(text(table_info_sql))
            columns = result.fetchall()
            column_names = [col[0] for col in columns]
            print(f"🔍 [MUSIC_TEAM_SEEKERS] 실제 테이블 컬럼: {column_names}")
        except Exception as e:
            print(f"⚠️ [MUSIC_TEAM_SEEKERS] 테이블 구조 확인 실패: {e}")
            column_names = []
        
        # Raw SQL INSERT (실제 컬럼명 사용)
        insert_sql = """
            INSERT INTO music_team_seekers (
                title, team_name, instrument, experience, portfolio,
                preferred_location, available_days, available_time,
                contact_phone, contact_email, status,
                author_id, author_name, church_id, church_name,
                view_count, likes, matches, applications
            ) VALUES (
                :title, :team_name, :instrument, :experience, :portfolio,
                :preferred_location, :available_days, :available_time,
                :contact_phone, :contact_email, :status,
                :author_id, :author_name, :church_id, :church_name,
                :view_count, :likes, :matches, :applications
            ) RETURNING id
        """
        
        insert_params = {
            "title": seeker_data.get('title'),
            "team_name": seeker_data.get('team_name'),
            "instrument": seeker_data.get('instrument'),
            "experience": seeker_data.get('experience'),
            "portfolio": seeker_data.get('portfolio'),
            "preferred_location": preferred_location,  # 파싱된 배열 사용
            "available_days": available_days,  # 파싱된 배열 사용
            "available_time": seeker_data.get('available_time'),
            "contact_phone": seeker_data.get('contact_phone'),
            "contact_email": seeker_data.get('contact_email'),
            "status": map_frontend_status_to_enum("available").value,  # 기본 상태
            "author_id": current_user.id,
            "author_name": current_user.full_name or "익명",
            "church_id": getattr(current_user, 'church_id', None),
            "church_name": getattr(current_user, 'church_name', None),
            "views": 0,       # 프론트엔드 호환성을 위한 views 필드
            "view_count": 0,  # views → view_count
            "likes": 0,
            "matches": 0,
            "applications": 0
        }
        
        print(f"🔍 [MUSIC_TEAM_SEEKERS] Raw SQL로 지원서 저장 중...")
        result = db.execute(text(insert_sql), insert_params)
        new_id = result.fetchone()[0]
        db.commit()
        print(f"✅ [MUSIC_TEAM_SEEKERS] 성공적으로 저장됨. ID: {new_id}")
        
        return {
            "success": True,
            "message": "지원서가 성공적으로 등록되었습니다",
            "data": {
                "id": new_id
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ [MUSIC_TEAM_SEEKERS] 등록 실패: {str(e)}")
        import traceback
        print(f"❌ [MUSIC_TEAM_SEEKERS] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "message": f"지원서 등록 중 오류가 발생했습니다: {str(e)}"
        }


@router.post("/music-team-seekers/{seeker_id}/increment-view", response_model=dict)
def increment_music_team_seeker_view_count(
    seeker_id: int,
    db: Session = Depends(get_db)
):
    """음악팀 지원자 조회수 증가 전용 API - 인증 없이 사용 가능"""
    try:
        from sqlalchemy import text
        print(f"🚀 [VIEW_INCREMENT_API] 음악팀 지원자 조회수 증가 전용 API 호출 - ID: {seeker_id}")

        # 현재 조회수 확인
        check_sql = "SELECT view_count FROM music_team_seekers WHERE id = :seeker_id"
        result = db.execute(text(check_sql), {"seeker_id": seeker_id})
        row = result.fetchone()

        if not row:
            return {
                "success": False,
                "message": "해당 음악팀 지원자를 찾을 수 없습니다."
            }

        current_view_count = row[0] or 0
        print(f"🔍 [VIEW_INCREMENT_API] 현재 조회수: {current_view_count}")

        # 조회수 증가
        increment_sql = """
            UPDATE music_team_seekers
            SET view_count = COALESCE(view_count, 0) + 1
            WHERE id = :seeker_id
            RETURNING view_count
        """
        result = db.execute(text(increment_sql), {"seeker_id": seeker_id})
        new_view_count = result.fetchone()[0]
        db.commit()

        print(f"✅ [VIEW_INCREMENT_API] 조회수 증가 성공 - ID: {seeker_id}, {current_view_count} → {new_view_count}")

        return {
            "success": True,
            "data": {
                "seeker_id": seeker_id,
                "previous_view_count": current_view_count,
                "new_view_count": new_view_count
            }
        }

    except Exception as e:
        db.rollback()
        print(f"❌ [VIEW_INCREMENT_API] 조회수 증가 실패 - ID: {seeker_id}, 오류: {e}")
        return {
            "success": False,
            "message": f"조회수 증가 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/music-team-seekers/{seeker_id}", response_model=dict)
def get_music_team_seeker_detail(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 상세 조회"""
    try:
        # Raw SQL로 안전한 조회
        from sqlalchemy import text
        db.rollback()  # 이전 트랜잭션 실패 방지
        
        query_sql = """
            SELECT 
                mts.id, mts.title, mts.team_name, mts.instrument, mts.experience,
                mts.portfolio, mts.preferred_location, mts.available_days,
                mts.available_time, mts.contact_phone, mts.contact_email,
                mts.status, mts.author_id, mts.author_name, mts.church_id, mts.church_name,
                mts.view_count, mts.likes, mts.matches, mts.applications,
                mts.created_at, mts.updated_at
            FROM music_team_seekers mts
            WHERE mts.id = :seeker_id
        """
        
        result = db.execute(text(query_sql), {"seeker_id": seeker_id})
        seeker_data = result.fetchone()
        if not seeker_data:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 조회수 증가는 별도 increment-view API에서만 처리
        
        # 배열 필드 처리
        preferred_location = seeker_data[6] if seeker_data[6] else []
        available_days = seeker_data[7] if seeker_data[7] else []
        
        return {
            "success": True,
            "data": {
                "id": seeker_data[0],
                "title": seeker_data[1],
                "team_name": seeker_data[2] or "",
                "instrument": seeker_data[3] or "",
                "experience": seeker_data[4] or "",
                "portfolio": seeker_data[5] or "",
                "preferred_location": preferred_location,
                "available_days": available_days,
                "available_time": seeker_data[8] or "",
                "contact_phone": seeker_data[9] or "",
                "contact_email": seeker_data[10] or "",
                "status": seeker_data[11] or "available",
                "author_id": seeker_data[12],
                "author_name": seeker_data[13] or "익명",
                "church_id": seeker_data[14] or 9998,
                "church_name": seeker_data[15] or "커뮤니티",
                "views": seeker_data[16] or 0,  # 실제 조회수 (증가 없음)
                "view_count": seeker_data[16] or 0,  # 프론트엔드 호환성을 위한 view_count 필드
                "likes": seeker_data[17] or 0,
                "matches": seeker_data[18] or 0,
                "applications": seeker_data[19] or 0,
                "created_at": seeker_data[20].isoformat() if seeker_data[20] else None,
                "updated_at": seeker_data[21].isoformat() if seeker_data[21] else None
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"지원서 상세 조회 중 오류가 발생했습니다: {str(e)}"
        }


@router.put("/music-team-seekers/{seeker_id}", response_model=dict)
async def update_music_team_seeker(
    seeker_id: int,
    seeker_data: MusicTeamSeekerUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 수정"""
    try:
        # Raw SQL로 안전한 조회 및 권한 확인
        from sqlalchemy import text
        db.rollback()
        
        # 작성자 확인 및 데이터 조회
        check_sql = """
            SELECT author_id, title 
            FROM music_team_seekers 
            WHERE id = :seeker_id
        """
        result = db.execute(text(check_sql), {"seeker_id": seeker_id})
        seeker_check = result.fetchone()
        if not seeker_check:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인
        if seeker_check[0] != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 지원서만 수정할 수 있습니다."
            }
        
        # 수정 가능한 필드 업데이트 (None이 아닌 값만)
        update_data = seeker_data.dict(exclude_unset=True)
        
        # Raw SQL UPDATE 문 생성 (updated_at는 SQLAlchemy onupdate=func.now()로 자동 처리)
        update_fields = []
        update_params = {"seeker_id": seeker_id}
        
        for field, value in update_data.items():
            if field in ['preferred_location', 'available_days'] and value is not None:
                update_fields.append(f"{field} = :{field}")
                update_params[field] = value if value else []
            elif value is not None:
                update_fields.append(f"{field} = :{field}")
                update_params[field] = value
        
        if update_fields:
            # updated_at는 SQLAlchemy의 onupdate=func.now()로 자동 처리됨
            update_sql = f"""
                UPDATE music_team_seekers 
                SET {', '.join(update_fields)}
                WHERE id = :seeker_id
                RETURNING title
            """
            
            result = db.execute(text(update_sql), update_params)
            updated_title = result.fetchone()[0]
            db.commit()
            
            return {
                "success": True,
                "message": "지원서가 수정되었습니다.",
                "data": {
                    "id": seeker_id,
                    "title": updated_title
                }
            }
        else:
            return {
                "success": True,
                "message": "수정할 내용이 없습니다.",
                "data": {
                    "id": seeker_id,
                    "title": seeker_check[1]
                }
            }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"지원서 수정 중 오류가 발생했습니다: {str(e)}"
        }


@router.delete("/music-team-seekers/{seeker_id}", response_model=dict)
def delete_music_team_seeker(
    seeker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """음악팀 지원서 삭제"""
    try:
        # Raw SQL로 안전한 조회 및 권한 확인
        from sqlalchemy import text
        db.rollback()
        
        # 작성자 확인
        check_sql = """
            SELECT author_id 
            FROM music_team_seekers 
            WHERE id = :seeker_id
        """
        result = db.execute(text(check_sql), {"seeker_id": seeker_id})
        seeker_check = result.fetchone()
        
        if not seeker_check:
            return {
                "success": False,
                "message": "지원서를 찾을 수 없습니다."
            }
        
        # 작성자 권한 확인
        if seeker_check[0] != current_user.id:
            return {
                "success": False,
                "message": "본인이 작성한 지원서만 삭제할 수 있습니다."
            }
        
        # Raw SQL DELETE
        delete_sql = "DELETE FROM music_team_seekers WHERE id = :seeker_id"
        db.execute(text(delete_sql), {"seeker_id": seeker_id})
        db.commit()
        
        return {
            "success": True,
            "message": "지원서가 삭제되었습니다."
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"지원서 삭제 중 오류가 발생했습니다: {str(e)}"
        }