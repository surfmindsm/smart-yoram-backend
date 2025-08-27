#!/usr/bin/env python3
"""
원격 서버에서 데모 데이터를 생성하는 스크립트
"""
import os
import sys

# 환경변수 확인
if not os.getenv('DATABASE_URL') or 'sqlite' in os.getenv('DATABASE_URL', ''):
    print("⚠️  경고: 이 스크립트는 운영 서버(PostgreSQL/Supabase)에서 실행해야 합니다.")
    print(f"현재 DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    
    # 로컬에서 실행하는 경우 확인 요청
    if input("그래도 계속하시겠습니까? (y/N): ").lower() != 'y':
        print("중단되었습니다.")
        sys.exit(1)

# 메인 데모 데이터 생성 스크립트 import 및 실행
from create_demo_data import create_demo_data

if __name__ == "__main__":
    print("🚀 운영 서버에서 데모 데이터 생성을 시작합니다...")
    create_demo_data()
    print("✅ 운영 서버 데모 데이터 생성 완료!")