#!/bin/bash

# 커뮤니티 플랫폼 마이그레이션 배포 스크립트
# 프로덕션 서버에서 실행해야 합니다

echo "=== Smart Yoram Community Platform Migration ==="
echo "현재 시간: $(date)"

# 1. 현재 마이그레이션 상태 확인
echo "1. 현재 마이그레이션 상태 확인..."
python3 -m alembic current

# 2. 대기 중인 마이그레이션 확인
echo -e "\n2. 대기 중인 마이그레이션 확인..."
python3 -m alembic heads

# 3. 커뮤니티 플랫폼 마이그레이션 실행
echo -e "\n3. 커뮤니티 플랫폼 마이그레이션 실행..."
python3 -m alembic upgrade community_platform_001

# 4. 마이그레이션 완료 후 상태 확인
echo -e "\n4. 마이그레이션 완료 후 상태 확인..."
python3 -m alembic current

# 5. 테이블 생성 확인 (PostgreSQL)
echo -e "\n5. 생성된 테이블 확인..."
psql $DATABASE_URL -c "
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'community_sharing',
    'community_requests', 
    'job_posts',
    'job_seekers',
    'music_team_recruits',
    'music_team_applications',
    'church_events'
)
ORDER BY table_name;
"

echo -e "\n=== 마이그레이션 완료 ==="
echo "완료 시간: $(date)"