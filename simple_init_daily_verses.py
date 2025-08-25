#!/usr/bin/env python3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.core.config import settings


def init_daily_verses():
    """초기 말씀 데이터 생성"""

    engine = create_engine(settings.DATABASE_URL)

    # 이미 데이터가 있는지 확인
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM daily_verses"))
        count = result.scalar()

        if count > 0:
            print(f"이미 {count}개의 말씀이 있습니다.")
            return

    # SQL 파일 읽기
    with open("init_daily_verses.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()

    # 데이터 삽입
    with engine.connect() as conn:
        conn.execute(text(sql_content))
        conn.commit()

    print("초기 말씀 데이터가 성공적으로 추가되었습니다.")


if __name__ == "__main__":
    init_daily_verses()
