#!/bin/bash

# Nginx가 이미 실행 중일 때 설정 업데이트하는 스크립트

echo "=== Nginx 설정 업데이트 (이미 실행 중) ==="
echo ""
echo "EC2에서 다음 명령어를 실행하세요:"
echo ""

cat << 'EOF'
# 1. 현재 Nginx 상태 확인
sudo systemctl status nginx

# 2. 현재 설정 확인
ls -la /etc/nginx/sites-enabled/

# 3. 기존 설정 백업
sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup 2>/dev/null || echo "기본 설정 없음"

# 4. Smart Yoram Nginx 설정 복사
cd ~/smart-yoram/smart-yoram-backend
sudo cp deploy/nginx-simple.conf /etc/nginx/sites-available/smartyoram

# 5. 기존 심볼릭 링크 제거 (있으면)
sudo rm -f /etc/nginx/sites-enabled/smartyoram

# 6. 새 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/

# 7. 기본 설정 제거
sudo rm -f /etc/nginx/sites-enabled/default

# 8. Nginx 설정 테스트
sudo nginx -t

# 9. Nginx 리로드 (재시작 아님)
sudo systemctl reload nginx

# 10. 테스트
curl http://localhost
curl http://localhost/docs

echo ""
echo "=== 설정 완료! ==="
echo "외부에서 접속: http://$(curl -s ifconfig.me)"
EOF

echo ""
echo "만약 에러가 발생하면:"
echo "1. sudo systemctl stop nginx"
echo "2. sudo systemctl start nginx"
echo "3. sudo journalctl -u nginx -n 50"