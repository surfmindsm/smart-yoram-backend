#!/usr/bin/env python3
"""
무료 나눔 상태값 단순화 마이그레이션 스크립트

변경 내용:
- available, reserved → sharing (나눔중)
- completed → completed (나눔완료)
- 기타 → sharing (기본값)
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

def migrate_sharing_status():
    """무료 나눔 상태값 마이그레이션 실행"""

    # 데이터베이스 연결
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("🚀 무료 나눔 상태값 마이그레이션 시작")

        # 1. 현재 상태값 분포 확인
        print("\n📊 현재 상태값 분포:")
        current_status_sql = """
            SELECT status, COUNT(*) as count
            FROM community_sharing
            GROUP BY status
            ORDER BY count DESC
        """
        result = db.execute(text(current_status_sql))
        current_statuses = result.fetchall()

        for status, count in current_statuses:
            print(f"  {status}: {count}개")

        # 2. 마이그레이션 실행
        print("\n🔄 상태값 마이그레이션 실행...")

        migration_sql = """
            UPDATE community_sharing
            SET status = CASE
                WHEN status IN ('available', 'reserved', 'active', 'paused') THEN 'sharing'
                WHEN status = 'completed' THEN 'completed'
                WHEN status IS NULL THEN 'sharing'
                ELSE 'sharing'
            END;
        """

        result = db.execute(text(migration_sql))
        updated_count = result.rowcount
        db.commit()

        print(f"✅ {updated_count}개 레코드 업데이트 완료")

        # 3. 마이그레이션 후 상태값 분포 확인
        print("\n📊 마이그레이션 후 상태값 분포:")
        result = db.execute(text(current_status_sql))
        new_statuses = result.fetchall()

        for status, count in new_statuses:
            print(f"  {status}: {count}개")

        # 4. 검증: 새로운 상태값만 존재하는지 확인
        validation_sql = """
            SELECT COUNT(*) as invalid_count
            FROM community_sharing
            WHERE status NOT IN ('sharing', 'completed')
        """
        result = db.execute(text(validation_sql))
        invalid_count = result.scalar()

        if invalid_count == 0:
            print("\n✅ 마이그레이션 검증 통과: 모든 상태값이 올바르게 변경됨")
        else:
            print(f"\n❌ 마이그레이션 검증 실패: {invalid_count}개의 잘못된 상태값 발견")

            # 잘못된 상태값 출력
            invalid_sql = """
                SELECT DISTINCT status
                FROM community_sharing
                WHERE status NOT IN ('sharing', 'completed')
            """
            result = db.execute(text(invalid_sql))
            invalid_statuses = [row[0] for row in result.fetchall()]
            print(f"  잘못된 상태값들: {invalid_statuses}")

        print("\n🎉 무료 나눔 상태값 마이그레이션 완료!")

    except Exception as e:
        print(f"\n❌ 마이그레이션 오류: {str(e)}")
        db.rollback()
        return False

    finally:
        db.close()

    return True

def rollback_sharing_status():
    """마이그레이션 롤백 (필요시 사용)"""

    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("🔄 무료 나눔 상태값 마이그레이션 롤백 시작")

        # sharing → available, completed는 그대로 유지
        rollback_sql = """
            UPDATE community_sharing
            SET status = CASE
                WHEN status = 'sharing' THEN 'available'
                WHEN status = 'completed' THEN 'completed'
                ELSE status
            END;
        """

        result = db.execute(text(rollback_sql))
        updated_count = result.rowcount
        db.commit()

        print(f"✅ {updated_count}개 레코드 롤백 완료")
        print("🎉 마이그레이션 롤백 완료!")

    except Exception as e:
        print(f"❌ 롤백 오류: {str(e)}")
        db.rollback()
        return False

    finally:
        db.close()

    return True

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="무료 나눔 상태값 마이그레이션")
    parser.add_argument("--rollback", action="store_true", help="마이그레이션 롤백")
    args = parser.parse_args()

    if args.rollback:
        success = rollback_sharing_status()
    else:
        success = migrate_sharing_status()

    sys.exit(0 if success else 1)