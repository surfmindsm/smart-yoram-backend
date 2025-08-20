from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.crud.crud_daily_verse import daily_verse as crud_daily_verse

router = APIRouter()


@router.get("/random", response_model=schemas.DailyVerse, summary="오늘의 말씀 랜덤 조회")
def get_random_daily_verse(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    오늘의 말씀을 랜덤으로 조회합니다.

    - **인증 불필요**: 누구나 접근 가능
    - **용도**: 모바일 앱이나 웹사이트 메인 화면에 표시
    - **응답**: 활성화된 말씀 중 랜덤하게 하나 반환
    """
    verse = crud_daily_verse.get_random_verse(db)
    if not verse:
        raise HTTPException(status_code=404, detail="활성화된 말씀이 없습니다.")
    return verse


@router.get("/", response_model=List[schemas.DailyVerse], summary="말씀 목록 조회")
def read_daily_verses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    등록된 모든 말씀 목록을 조회합니다.

    - **권한**: 관리자만 접근 가능
    - **페이지네이션**: skip과 limit 매개변수 지원
    - **정렬**: 최신 등록순
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    verses = crud_daily_verse.get_all_verses(db, skip=skip, limit=limit)
    return verses


@router.post("/", response_model=schemas.DailyVerse, summary="새 말씀 추가")
def create_daily_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_in: schemas.DailyVerseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    새로운 성경 말씀을 추가합니다.

    - **권한**: 관리자만 접근 가능
    - **verse**: 성경 구절 내용
    - **reference**: 출처 (예: 시편 23:1)
    - **is_active**: 활성화 여부 (기본값: true)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    verse = crud_daily_verse.create(db=db, obj_in=verse_in)
    return verse


@router.put("/{verse_id}", response_model=schemas.DailyVerse)
def update_daily_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_id: int,
    verse_in: schemas.DailyVerseUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    말씀 수정 (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    verse = crud_daily_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="말씀을 찾을 수 없습니다.")

    verse = crud_daily_verse.update(db=db, db_obj=verse, obj_in=verse_in)
    return verse


@router.delete("/{verse_id}", response_model=schemas.DailyVerse)
def delete_daily_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    말씀 삭제 (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    verse = crud_daily_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="말씀을 찾을 수 없습니다.")

    verse = crud_daily_verse.remove(db=db, id=verse_id)
    return verse


@router.get("/stats", response_model=dict, summary="말씀 통계 조회")
def get_daily_verse_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    오늘의 말씀 통계를 조회합니다.

    - **권한**: 관리자만 접근 가능
    - **total_verses**: 전체 말씀 개수
    - **active_verses**: 활성화된 말씀 개수
    - **inactive_verses**: 비활성화된 말씀 개수
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")

    total_count = crud_daily_verse.count_verses(db)
    active_count = crud_daily_verse.count_active_verses(db)

    return {
        "total_verses": total_count,
        "active_verses": active_count,
        "inactive_verses": total_count - active_count,
    }
