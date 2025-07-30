#!/bin/bash

# Docker 컨테이너 문제 디버깅 스크립트

echo "=== Docker Container 디버깅 ==="
echo ""

# 1. 컨테이너 로그 확인
echo "1. 최근 로그 확인:"
docker-compose logs --tail=50 backend

echo ""
echo "2. 컨테이너 상세 정보:"
docker inspect smart-yoram-backend_backend_1 | grep -A 10 "Health"

echo ""
echo "3. 컨테이너 내부에서 헬스체크:"
docker-compose exec backend curl -f http://localhost:8000/ || echo "헬스체크 실패"

echo ""
echo "4. 환경 변수 확인 (.env 파일 존재 여부):"
if [ -f .env ]; then
    echo ".env 파일 존재 ✓"
    echo "DATABASE_URL 설정 확인:"
    grep "DATABASE_URL" .env | sed 's/password=.*/password=***/'
else
    echo ".env 파일 없음! ✗"
    echo ".env.example을 복사하고 설정해주세요:"
    echo "cp .env.example .env"
    echo "nano .env"
fi

echo ""
echo "5. 포트 바인딩 확인:"
netstat -tlnp 2>/dev/null | grep 8000 || sudo lsof -i :8000

echo ""
echo "=== 일반적인 해결 방법 ==="
echo ""
echo "1. 컨테이너 재시작:"
echo "   docker-compose restart"
echo ""
echo "2. 컨테이너 재빌드:"
echo "   docker-compose down"
echo "   docker-compose up -d --build"
echo ""
echo "3. 로그 실시간 확인:"
echo "   docker-compose logs -f backend"