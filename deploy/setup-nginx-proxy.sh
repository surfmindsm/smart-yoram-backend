#!/bin/bash

# EC2에서 Nginx를 설정하여 80포트를 8000포트로 프록시하는 스크립트

echo "=== Nginx Proxy Setup (80 -> 8000) ==="
echo ""
echo "EC2에서 다음 명령어를 실행하세요:"
echo ""

cat << 'EOF'
# 1. Nginx 설치 확인
sudo apt update
sudo apt install -y nginx

# 2. 기본 Nginx 설정 백업
sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup

# 3. Smart Yoram Nginx 설정 복사
cd ~/smart-yoram/smart-yoram-backend
sudo cp deploy/nginx-simple.conf /etc/nginx/sites-available/smartyoram

# 4. 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/

# 5. 기본 설정 제거
sudo rm /etc/nginx/sites-enabled/default

# 6. Nginx 설정 테스트
sudo nginx -t

# 7. Nginx 재시작
sudo systemctl restart nginx

# 8. Nginx 상태 확인
sudo systemctl status nginx

# 9. 방화벽 설정 (이미 열려있을 수 있음)
sudo ufw allow 'Nginx Full'
sudo ufw allow 80/tcp
sudo ufw status

# 10. 테스트
echo ""
echo "=== 설정 완료! ==="
echo "이제 다음 주소로 접속 가능합니다:"
echo "http://$(curl -s ifconfig.me)"
echo "http://$(curl -s ifconfig.me)/docs"
EOF

echo ""
echo "주의사항:"
echo "1. Docker 컨테이너가 실행 중이어야 합니다 (port 8000)"
echo "2. EC2 Security Group에서 80번 포트가 열려있어야 합니다"
echo "3. 8000번 포트는 이제 닫아도 됩니다 (선택사항)"