from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/random", response_model=schemas.DailyVerse)
def get_random_daily_verse(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    오늘의 말씀 랜덤 조회 (인증 불필요)
    """
    verse = crud.daily_verse.get_random_verse(db)
    if not verse:
        raise HTTPException(
            status_code=404,
            detail="활성화된 말씀이 없습니다."
        )
    return verse


@router.get("/", response_model=List[schemas.DailyVerse])
def read_daily_verses(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    말씀 목록 조회 (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    verses = crud.daily_verse.get_all_verses(db, skip=skip, limit=limit)
    return verses


@router.post("/", response_model=schemas.DailyVerse)
def create_daily_verse(
    *,
    db: Session = Depends(deps.get_db),
    verse_in: schemas.DailyVerseCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    새 말씀 생성 (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    verse = crud.daily_verse.create(db=db, obj_in=verse_in)
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
    
    verse = crud.daily_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="말씀을 찾을 수 없습니다.")
    
    verse = crud.daily_verse.update(db=db, db_obj=verse, obj_in=verse_in)
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
    
    verse = crud.daily_verse.get(db=db, id=verse_id)
    if not verse:
        raise HTTPException(status_code=404, detail="말씀을 찾을 수 없습니다.")
    
    verse = crud.daily_verse.remove(db=db, id=verse_id)
    return verse


@router.get("/stats", response_model=dict)
def get_daily_verse_stats(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    말씀 통계 조회 (관리자 전용)
    """
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="권한이 없습니다.")
    
    total_count = crud.daily_verse.count_verses(db)
    active_count = crud.daily_verse.count_active_verses(db)
    
    return {
        "total_verses": total_count,
        "active_verses": active_count,
        "inactive_verses": total_count - active_count
    }