#!/bin/bash

# Nginx 설정 문제 해결 스크립트

echo "=== Nginx 설정 문제 해결 ==="
echo ""

# 1. 현재 설정 확인
echo "1. 현재 Nginx 설정 파일 확인:"
sudo cat /etc/nginx/sites-available/smartyoram | head -20
echo ""

# 2. 설정 파일이 제대로 복사되었는지 확인
echo "2. nginx-simple.conf 파일 확인:"
if [ -f deploy/nginx-simple.conf ]; then
    echo "파일 존재 ✓"
    echo "내용:"
    cat deploy/nginx-simple.conf | head -10
else
    echo "파일 없음 ✗"
fi
echo ""

# 3. 기본 설정 파일 제거 확인
echo "3. 기본 설정 제거:"
sudo rm -f /etc/nginx/sites-enabled/default
sudo rm -f /etc/nginx/sites-enabled/default.backup

# 4. 설정 다시 복사
echo ""
echo "4. 설정 다시 복사:"
sudo cp deploy/nginx-simple.conf /etc/nginx/sites-available/smartyoram
sudo ln -sf /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/smartyoram

# 5. sites-enabled 확인
echo ""
echo "5. sites-enabled 디렉토리:"
ls -la /etc/nginx/sites-enabled/

# 6. Nginx 설정 테스트
echo ""
echo "6. Nginx 설정 테스트:"
sudo nginx -t

# 7. Nginx 재시작 (reload가 아닌 restart)
echo ""
echo "7. Nginx 재시작:"
sudo systemctl restart nginx

# 8. 프로세스 확인
echo ""
echo "8. Nginx 프로세스:"
ps aux | grep nginx | head -5

# 9. 테스트
echo ""
echo "9. 프록시 테스트:"
sleep 2
curl -I http://localhost/ 2>&1 | head -10

echo ""
echo "10. Docker 상태:"
docker-compose ps

echo ""
echo "=== 완료 ==="
echo "브라우저에서 다시 테스트: http://$(curl -s ifconfig.me)/"