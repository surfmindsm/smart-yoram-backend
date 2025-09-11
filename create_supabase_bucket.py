#!/usr/bin/env python3
"""
Supabase community-images 버킷 생성 스크립트

이 스크립트를 실행하기 전에:
1. Supabase 대시보드 (https://app.supabase.com) 접속
2. 프로젝트 선택
3. Storage > Buckets로 이동
4. "New bucket" 버튼 클릭
5. 다음 설정으로 생성:
   - Name: community-images
   - Public: Yes
   - File size limit: 50MB
   - MIME types: image/jpeg, image/png, image/gif, image/webp

이 스크립트는 버킷 생성 확인 및 테스트 업로드를 수행합니다.
"""

import os
import tempfile
from dotenv import load_dotenv
from app.utils.storage import supabase, COMMUNITY_IMAGES_BUCKET

def main():
    load_dotenv()
    
    print("🗂️  Supabase community-images 버킷 설정 확인")
    print("=" * 60)
    
    try:
        # 1. 연결 테스트
        print("1️⃣  Supabase 연결 테스트...")
        buckets = supabase.storage.list_buckets()
        bucket_names = [b.get('name') for b in buckets]
        print(f"   ✅ 연결 성공! 사용 가능한 버킷: {bucket_names}")
        
        # 2. community-images 버킷 확인
        print(f"\n2️⃣  {COMMUNITY_IMAGES_BUCKET} 버킷 확인...")
        if COMMUNITY_IMAGES_BUCKET in bucket_names:
            print(f"   ✅ {COMMUNITY_IMAGES_BUCKET} 버킷이 존재합니다!")
            
            # 3. 테스트 업로드
            print(f"\n3️⃣  테스트 업로드 수행...")
            test_content = b"TEST_IMAGE_CONTENT_FOR_COMMUNITY_UPLOAD"
            test_filename = "test_church_9998_upload.txt"
            test_path = f"church_9998/{test_filename}"
            
            try:
                # 업로드 테스트
                result = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).upload(
                    path=test_path,
                    file=test_content,
                    file_options={"content-type": "text/plain"}
                )
                
                if hasattr(result, 'error') and result.error:
                    print(f"   ❌ 테스트 업로드 실패: {result.error.message}")
                else:
                    print(f"   ✅ 테스트 업로드 성공!")
                    
                    # URL 생성 테스트
                    public_url = supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).get_public_url(test_path)
                    print(f"   📎 생성된 URL: {public_url}")
                    
                    # 테스트 파일 정리
                    try:
                        supabase.storage.from_(COMMUNITY_IMAGES_BUCKET).remove([test_path])
                        print(f"   🧹 테스트 파일 정리 완료")
                    except:
                        print(f"   ⚠️  테스트 파일 정리 실패 (수동 삭제 필요)")
                        
            except Exception as upload_error:
                print(f"   ❌ 테스트 업로드 중 오류: {upload_error}")
                
        else:
            print(f"   ❌ {COMMUNITY_IMAGES_BUCKET} 버킷이 없습니다!")
            print(f"\n📋 수동 생성 방법:")
            print(f"   1. https://app.supabase.com 접속")
            print(f"   2. 프로젝트 선택")
            print(f"   3. Storage > Buckets")
            print(f"   4. 'New bucket' 클릭")
            print(f"   5. 설정:")
            print(f"      - Name: {COMMUNITY_IMAGES_BUCKET}")
            print(f"      - Public: Yes")
            print(f"      - File size limit: 50MB")
            print(f"      - MIME types: image/jpeg, image/png, image/gif, image/webp")
            
    except Exception as e:
        print(f"❌ 전체 프로세스 실패: {e}")
        
    print("\n" + "=" * 60)
    print("🎯 완료!")

if __name__ == "__main__":
    main()