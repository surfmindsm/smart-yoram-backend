#!/bin/bash

# Nginx 프록시 테스트 스크립트

echo "=== Nginx 프록시 테스트 ==="
echo ""

# 1. Docker 컨테이너 직접 테스트
echo "1. Docker 컨테이너 직접 테스트 (8000 포트):"
curl -I http://localhost:8000/
echo ""

# 2. Nginx 프록시 테스트
echo "2. Nginx 프록시 테스트 (80 포트):"
curl -I http://localhost/
echo ""

# 3. API 문서 테스트
echo "3. API 문서 테스트:"
curl -I http://localhost/docs
echo ""

# 4. 실제 API 엔드포인트 테스트
echo "4. API 엔드포인트 테스트:"
curl http://localhost/api/v1/health
echo ""

# 5. Nginx 설정 확인
echo "5. 현재 Nginx 설정:"
ls -la /etc/nginx/sites-enabled/
echo ""

# 6. Nginx 에러 로그 확인
echo "6. Nginx 최근 에러 로그:"
sudo tail -5 /var/log/nginx/smartyoram_error.log 2>/dev/null || echo "에러 로그 없음"
echo ""

# 7. 외부 IP
EXTERNAL_IP=$(curl -s ifconfig.me)
echo "7. 외부 접속 주소:"
echo "   http://$EXTERNAL_IP/"
echo "   http://$EXTERNAL_IP/docs"