from typing import List, Optional
import random
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.crud.base import CRUDBase
from app.models.daily_verse import DailyVerse
from app.schemas.daily_verse import DailyVerseCreate, DailyVerseUpdate


class CRUDDailyVerse(CRUDBase[DailyVerse, DailyVerseCreate, DailyVerseUpdate]):
    def get_random_verse(self, db: Session) -> Optional[DailyVerse]:
        """활성화된 말씀 중에서 랜덤하게 하나를 선택"""
        active_verses = db.query(DailyVerse).filter(DailyVerse.is_active == True).all()
        if not active_verses:
            return None
        return random.choice(active_verses)
    
    def get_active_verses(self, db: Session, skip: int = 0, limit: int = 100) -> List[DailyVerse]:
        """활성화된 말씀 목록 조회"""
        return (
            db.query(DailyVerse)
            .filter(DailyVerse.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_all_verses(self, db: Session, skip: int = 0, limit: int = 100) -> List[DailyVerse]:
        """모든 말씀 목록 조회 (관리용)"""
        return (
            db.query(DailyVerse)
            .order_by(DailyVerse.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def count_verses(self, db: Session) -> int:
        """전체 말씀 개수"""
        return db.query(DailyVerse).count()
    
    def count_active_verses(self, db: Session) -> int:
        """활성화된 말씀 개수"""
        return db.query(DailyVerse).filter(DailyVerse.is_active == True).count()


daily_verse = CRUDDailyVerse(DailyVerse)