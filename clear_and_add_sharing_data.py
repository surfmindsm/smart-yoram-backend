#!/usr/bin/env python3

"""
community_sharing 테이블 데이터 삭제 후 새로 추가
"""

import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from app.core.config import settings
import json
from datetime import datetime, timezone

def clear_and_add_data():
    """기존 데이터 삭제 후 새로운 데이터 추가"""

    try:
        # 데이터베이스 연결
        engine = create_engine(str(settings.DATABASE_URL))

        with engine.connect() as conn:
            # 트랜잭션 시작
            trans = conn.begin()

            try:
                # 1. 기존 데이터 삭제
                print("🗑️ 기존 community_sharing 데이터 삭제 중...")
                delete_result = conn.execute(text("DELETE FROM community_sharing"))
                deleted_count = delete_result.rowcount
                print(f"✅ {deleted_count}개 레코드 삭제됨")

                # 2. 새로운 데이터 추가 (API 컬럼 구조에 맞춤)
                sample_data = [
                    {
                        'title': '냉장고 무료 나눔',
                        'description': '이사가면서 냉장고를 무료로 나눔합니다. 상태 좋습니다.',
                        'category': '가전제품',
                        'condition': 'good',
                        'price': 0,
                        'is_free': True,
                        'location': '서울시 강남구',
                        'contact_phone': '010-1234-5678',
                        'contact_email': 'test1@example.com',
                        'images': '[]',
                        'status': 'available',
                        'view_count': 0,
                        'author_id': 20,  # 기존 사용자 ID 사용
                        'church_id': 6,   # 프론트엔드에서 사용하는 교회 ID
                        'likes': 0
                    },
                    {
                        'title': '책장 무료 드림',
                        'description': '원목 책장입니다. 직접 가져가실 분만 연락주세요.',
                        'category': '가구',
                        'condition': 'good',
                        'price': 0,
                        'is_free': True,
                        'location': '서울시 서초구',
                        'contact_phone': '010-2345-6789',
                        'contact_email': 'test2@example.com',
                        'images': '[]',
                        'status': 'available',
                        'view_count': 0,
                        'author_id': 20,
                        'church_id': 6,
                        'likes': 0
                    },
                    {
                        'title': '아기 옷 나눔',
                        'description': '6-12개월 아기 옷들 한 박스 나눔해요. 깨끗하게 세탁해서 드릴게요.',
                        'category': '의류',
                        'condition': 'excellent',
                        'price': 0,
                        'is_free': True,
                        'location': '서울시 송파구',
                        'contact_phone': '010-3456-7890',
                        'contact_email': 'test3@example.com',
                        'images': '[]',
                        'status': 'available',
                        'view_count': 0,
                        'author_id': 20,
                        'church_id': 6,
                        'likes': 0
                    }
                ]

                # 데이터 삽입 (API 컬럼명에 맞춤)
                insert_sql = """
                    INSERT INTO community_sharing (
                        title, description, category, condition, price, is_free,
                        location, contact_phone, contact_email, images, status,
                        view_count, author_id, church_id, likes, created_at, updated_at
                    ) VALUES (
                        :title, :description, :category, :condition, :price, :is_free,
                        :location, :contact_phone, :contact_email, :images, :status,
                        :view_count, :author_id, :church_id, :likes,
                        NOW(), NOW()
                    )
                """

                for i, data in enumerate(sample_data):
                    result = conn.execute(text(insert_sql), data)
                    print(f"✅ 새 무료나눔 데이터 {i+1} 추가됨: {data['title']}")

                # 커밋
                trans.commit()

                # 확인
                result = conn.execute(text("SELECT COUNT(*) FROM community_sharing WHERE is_free = true"))
                new_count = result.scalar()
                print(f"📊 무료나눔 데이터 개수: {new_count}")

                # 추가된 데이터 조회
                result = conn.execute(text("""
                    SELECT id, title, category, location, status, is_free, contact_phone
                    FROM community_sharing
                    WHERE is_free = true
                    ORDER BY created_at DESC
                """))
                rows = result.fetchall()

                print("\n📋 추가된 무료나눔 데이터:")
                for row in rows:
                    print(f"   ID: {row[0]}, 제목: {row[1]}, 카테고리: {row[2]}, 지역: {row[3]}, 상태: {row[4]}, 무료: {row[5]}, 연락처: {row[6]}")

                print("\n✅ 무료나눔 데이터 갱신 완료!")

            except Exception as e:
                trans.rollback()
                print(f"❌ 데이터 처리 중 오류: {e}")
                raise

    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {e}")

if __name__ == "__main__":
    print("🚀 community_sharing 테이블 데이터 갱신 시작")
    print("=" * 60)
    clear_and_add_data()
    print("🏁 완료")