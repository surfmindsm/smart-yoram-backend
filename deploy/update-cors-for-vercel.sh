#!/bin/bash

# EC2에서 CORS 설정 업데이트 스크립트

echo "=== CORS 설정 업데이트 (Vercel 추가) ==="
echo ""
echo "EC2에서 다음 명령어를 실행하세요:"
echo ""

cat << 'EOF'
# 1. 백엔드 디렉토리로 이동
cd ~/smart-yoram/smart-yoram-backend

# 2. .env 파일 백업
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

# 3. CORS 설정 업데이트
# Vercel 도메인 추가
sed -i 's/BACKEND_CORS_ORIGINS=.*/BACKEND_CORS_ORIGINS=["http:\/\/localhost:3000", "http:\/\/localhost:8080", "https:\/\/smart-yoram-admin.vercel.app"]/' .env

# 4. 설정 확인
echo "업데이트된 CORS 설정:"
grep "BACKEND_CORS_ORIGINS" .env

# 5. Docker 컨테이너 재시작
echo ""
echo "Docker 컨테이너 재시작 중..."
docker-compose restart

# 6. 로그 확인
echo ""
echo "로그 확인 (10초 대기):"
sleep 10
docker-compose logs --tail=20 backend

# 7. 헬스체크
echo ""
echo "헬스체크:"
curl http://localhost:8000/

echo ""
echo "=== 완료! ==="
echo "이제 https://smart-yoram-admin.vercel.app 에서 백엔드에 접속할 수 있습니다."
EOF

echo ""
echo "주의사항:"
echo "1. HTTPS (Vercel) → HTTP (EC2) 연결로 Mixed Content 문제가 발생할 수 있습니다"
echo "2. 브라우저 콘솔에서 에러를 확인하세요"
echo "3. 필요하면 EC2에 SSL 인증서를 설정하세요"