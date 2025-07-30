#!/bin/bash

# 새 CloudFlare Tunnel URL로 CORS 업데이트

echo "=== CORS 업데이트 (새 CloudFlare Tunnel) ==="
echo ""

NEW_TUNNEL_URL="https://rehabilitation-fonts-september-quizzes.trycloudflare.com"

# .env 파일 백업
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

# CORS 설정 업데이트
echo "1. CORS 설정 업데이트 중..."
sed -i 's|BACKEND_CORS_ORIGINS=.*|BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "https://smart-yoram-admin.vercel.app", "'$NEW_TUNNEL_URL'"]|' .env

# 설정 확인
echo ""
echo "2. 업데이트된 CORS 설정:"
grep "BACKEND_CORS_ORIGINS" .env

# Docker 재시작
echo ""
echo "3. Docker 컨테이너 재시작..."
docker-compose restart

# 대기
echo ""
echo "4. 컨테이너 시작 대기 중 (20초)..."
sleep 20

# 헬스체크
echo ""
echo "5. 헬스체크:"
echo "- 로컬: $(curl -s http://localhost:8000/)"
echo "- CloudFlare: $(curl -s $NEW_TUNNEL_URL/)"

echo ""
echo "=== ✓ 완료! ==="
echo "새 Tunnel URL: $NEW_TUNNEL_URL"
echo ""
echo "프론트엔드 배포:"
echo "git add . && git commit -m 'Update CloudFlare Tunnel URL' && git push"