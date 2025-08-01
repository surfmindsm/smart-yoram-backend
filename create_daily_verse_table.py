from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models.daily_verse import DailyVerse
from app.db.init_daily_verses import init_daily_verses
from app.db.session import SessionLocal

def create_table_and_init_data():
    """daily_verses 테이블 생성 및 초기 데이터 추가"""
    
    # 1. 테이블 생성
    engine = create_engine(settings.DATABASE_URL)
    
    # daily_verses 테이블만 생성
    DailyVerse.__table__.create(bind=engine, checkfirst=True)
    print("daily_verses 테이블이 생성되었습니다.")
    
    # 2. 초기 데이터 추가
    db = SessionLocal()
    try:
        # 테이블이 비어있는지 확인
        count = db.execute(text("SELECT COUNT(*) FROM daily_verses")).scalar()
        if count == 0:
            init_daily_verses(db)
            print("초기 말씀 데이터가 추가되었습니다.")
        else:
            print(f"이미 {count}개의 말씀이 있습니다.")
    finally:
        db.close()

if __name__ == "__main__":
    create_table_and_init_data()