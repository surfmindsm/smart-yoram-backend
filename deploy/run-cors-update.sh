#!/bin/bash

# EC2에서 CORS 설정 업데이트 (CloudFlare Tunnel 추가) - 실행 버전

echo "=== CORS 설정 업데이트 실행 중 ==="
echo ""

# 1. 백엔드 디렉토리로 이동
echo "1. 디렉토리 이동..."
cd ~/smart-yoram/smart-yoram-backend || exit 1

# 2. 최신 코드 받기
echo "2. 최신 코드 받는 중..."
git pull origin main

# 3. Docker 컨테이너 재시작
echo ""
echo "3. Docker 컨테이너 재시작 중..."
docker-compose down
docker-compose up -d

# 4. 로그 확인 (30초 대기)
echo ""
echo "4. 컨테이너 시작 대기 중 (30초)..."
sleep 30

# 5. 헬스체크
echo ""
echo "5. 헬스체크 (로컬):"
curl http://localhost:8000/
echo ""

echo ""
echo "6. 헬스체크 (CloudFlare):"
curl https://lloyd-kuwait-margaret-territory.trycloudflare.com/
echo ""

# 6. CORS 설정 확인
echo ""
echo "7. 현재 CORS 설정:"
grep "BACKEND_CORS_ORIGINS" .env

# 7. 로그 확인
echo ""
echo "8. 백엔드 로그 (최근 50줄):"
docker-compose logs --tail=50 backend

echo ""
echo "=== ✓ 완료! ==="
echo "이제 다음 URL들이 CORS 허용됩니다:"
echo "- https://smart-yoram-admin.vercel.app"
echo "- https://lloyd-kuwait-margaret-territory.trycloudflare.com"
echo ""
echo "참고: CloudFlare Tunnel URL은 재시작할 때마다 변경될 수 있습니다."