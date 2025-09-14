#!/usr/bin/env python3
"""
커뮤니티 테이블 표준화 마이그레이션 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text

def run_migration():
    # Supabase 데이터베이스 URL
    database_url = "postgresql://postgres.adzhdsajdamrflvybhxq:Windsurfsm24!@aws-0-ap-northeast-2.pooler.supabase.com:6543/postgres"
    
    engine = create_engine(database_url)
    
    print("🔄 커뮤니티 테이블 표준화 마이그레이션 시작...")
    
    # SQL 스크립트 읽기
    with open("scripts/standardize_community_tables.sql", "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    try:
        with engine.connect() as conn:
            # 세미콜론으로 분리된 각 명령어를 개별 실행
            commands = sql_content.split(';')
            
            for i, command in enumerate(commands):
                command = command.strip()
                if command and not command.startswith('--') and not command.startswith('/*'):
                    try:
                        print(f"📝 명령어 {i+1} 실행 중...")
                        result = conn.execute(text(command))
                        
                        # SELECT 결과가 있으면 출력
                        if command.upper().startswith('SELECT'):
                            rows = result.fetchall()
                            for row in rows:
                                print(f"   {row}")
                        
                        conn.commit()
                        print(f"✅ 명령어 {i+1} 완료")
                        
                    except Exception as e:
                        print(f"❌ 명령어 {i+1} 실패: {e}")
                        # 일부 오류는 무시하고 계속 진행 (테이블이 이미 존재하지 않는 경우 등)
                        if "does not exist" in str(e) or "already exists" in str(e):
                            print("   (예상된 오류 - 계속 진행)")
                            continue
                        else:
                            print("   (치명적 오류 - 중단)")
                            break
            
        print("✅ 마이그레이션 완료!")
        
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()