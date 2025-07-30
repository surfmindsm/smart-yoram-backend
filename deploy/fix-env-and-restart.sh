#!/bin/bash

# EC2에서 .env 파일 수정 및 Docker 완전 재시작

echo "=== .env 파일 수정 및 Docker 재시작 ==="
echo ""

# 1. 현재 .env 확인
echo "1. 현재 .env 파일 내용:"
cat .env | head -5
echo ""

# 2. .env 파일 백업
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

# 3. 새 .env 파일 생성
echo "2. 새 .env 파일 생성 중..."
cat > .env << 'EOF'
# Database (Supabase)
DATABASE_URL=postgresql://postgres.adzhdsajdamrflvybhxq:7Vhg9aJh5rv76zI7@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://adzhdsajdamrflvybhxq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkemhkc2FqZGFtcmZsdnliaHhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NDg5ODEsImV4cCI6MjA2OTQyNDk4MX0.pgn6M5_ihDFt3ojQmCoc3Qf8pc7LzRvQEIDT7g1nW3c

# Security
SECRET_KEY=smart-yoram-secret-key-2025-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "https://smart-yoram-admin.vercel.app", "https://packs-holds-marc-extended.trycloudflare.com"]

# Application
PROJECT_NAME="Smart Yoram API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
EOF

# 4. 새 .env 확인
echo ""
echo "3. 새 .env 파일 내용:"
cat .env | head -5
echo ""

# 5. Docker 완전 중지 및 재시작
echo "4. Docker 완전 재시작 중..."
docker-compose down
docker-compose up -d --build

# 6. 대기
echo ""
echo "5. 컨테이너 시작 대기 중 (30초)..."
sleep 30

# 7. 컨테이너 상태 확인
echo ""
echo "6. 컨테이너 상태:"
docker-compose ps

# 8. 데이터베이스 연결 테스트
echo ""
echo "7. 데이터베이스 연결 테스트:"
docker-compose exec backend python -c "
from app.db.session import SessionLocal
try:
    db = SessionLocal()
    db.execute('SELECT 1')
    print('✓ 데이터베이스 연결 성공!')
except Exception as e:
    print(f'✗ 데이터베이스 연결 실패: {e}')
"

# 9. 헬스체크
echo ""
echo "8. API 헬스체크:"
curl -s http://localhost:8000/ | jq . || curl -s http://localhost:8000/

# 10. 로그 확인
echo ""
echo "9. 최근 로그:"
docker-compose logs --tail=20 backend | grep -v "GET / HTTP"

echo ""
echo "=== 완료 ==="
echo ""
echo "만약 여전히 에러가 발생한다면:"
echo "1. docker-compose down -v  # 볼륨까지 삭제"
echo "2. docker-compose up -d --build  # 재빌드"