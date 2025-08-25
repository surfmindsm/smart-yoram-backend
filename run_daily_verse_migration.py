import subprocess
import sys
from app.db.init_daily_verses import init_daily_verses
from app.db.session import SessionLocal


def run_migration():
    """마이그레이션 실행 및 초기 데이터 생성"""
    try:
        # 1. 마이그레이션 실행
        print("데이터베이스 마이그레이션 실행 중...")
        result = subprocess.run(
            ["alembic", "upgrade", "head"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"마이그레이션 실패: {result.stderr}")
            return False

        print("마이그레이션 완료!")

        # 2. 초기 데이터 생성
        print("\n초기 말씀 데이터 생성 중...")
        db = SessionLocal()
        try:
            init_daily_verses(db)
            print("초기 데이터 생성 완료!")
        finally:
            db.close()

        return True

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
