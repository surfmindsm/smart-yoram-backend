#!/usr/bin/env python3
"""
무료나눔 데이터에 이미지 URL을 포함하여 테스트 데이터 추가
"""

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
import json

# 데이터베이스 URL (환경변수에서 가져오거나 직접 설정)
DATABASE_URL = "postgresql://postgres.azquvnxnhthkfzfscwsw:Hy5pBmGz2XrczXWz@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"

def main():
    print("🚀 이미지 URL이 포함된 무료나눔 테스트 데이터 추가 시작...")

    # 데이터베이스 연결
    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        # 기존 테스트 데이터가 있는지 확인
        check_sql = "SELECT id, title, images FROM community_sharing WHERE title LIKE '%이미지 테스트%' ORDER BY id"
        result = conn.execute(text(check_sql))
        existing_data = result.fetchall()

        print(f"📋 기존 이미지 테스트 데이터: {len(existing_data)}개")
        for row in existing_data:
            print(f"  - ID: {row[0]}, 제목: {row[1]}, 이미지: {row[2]}")

        # 새로운 테스트 데이터 추가
        test_images = [
            "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=500",
            "https://images.unsplash.com/photo-1549497538-303791108f95?w=500"
        ]

        images_json = json.dumps(test_images)
        print(f"📸 추가할 이미지 JSON: {images_json}")

        insert_sql = """
            INSERT INTO community_sharing (
                title, description, category, condition, price, is_free,
                location, contact_info, status, images, author_id, church_id,
                created_at, updated_at
            ) VALUES (
                :title, :description, :category, :condition, :price, :is_free,
                :location, :contact_info, :status, :images, :author_id, :church_id,
                NOW(), NOW()
            ) RETURNING id, images
        """

        params = {
            "title": "이미지 테스트 무료나눔",
            "description": "이미지 URL이 포함된 테스트 데이터입니다",
            "category": "가구",
            "condition": "양호",
            "price": 0,
            "is_free": True,
            "location": "서울시 강남구",
            "contact_info": "댓글로 연락주세요",
            "status": "ACTIVE",
            "images": images_json,
            "author_id": 54,  # test1 사용자 ID
            "church_id": 9998
        }

        result = conn.execute(text(insert_sql), params)
        row = result.fetchone()
        new_id = row[0]
        saved_images = row[1]

        conn.commit()

        print(f"✅ 새로운 데이터 추가 완료!")
        print(f"   - 새 ID: {new_id}")
        print(f"   - 저장된 이미지: {saved_images}")
        print(f"   - 저장된 이미지 타입: {type(saved_images)}")

        # 추가된 데이터 확인
        verify_sql = "SELECT id, title, images FROM community_sharing WHERE id = :id"
        verify_result = conn.execute(text(verify_sql), {"id": new_id})
        verify_row = verify_result.fetchone()

        if verify_row:
            print(f"🔍 저장 확인:")
            print(f"   - ID: {verify_row[0]}")
            print(f"   - 제목: {verify_row[1]}")
            print(f"   - 이미지 원본: {repr(verify_row[2])}")
            print(f"   - 이미지 타입: {type(verify_row[2])}")

            # JSON 파싱 테스트
            if isinstance(verify_row[2], str):
                try:
                    parsed_images = json.loads(verify_row[2])
                    print(f"   - JSON 파싱 성공: {parsed_images}")
                except Exception as e:
                    print(f"   - JSON 파싱 실패: {e}")
            elif isinstance(verify_row[2], list):
                print(f"   - 이미 리스트 형태: {verify_row[2]}")
            else:
                print(f"   - 알 수 없는 타입: {type(verify_row[2])}")

        print(f"🎉 이미지 URL이 포함된 무료나눔 데이터 추가 완료!")

if __name__ == "__main__":
    main()