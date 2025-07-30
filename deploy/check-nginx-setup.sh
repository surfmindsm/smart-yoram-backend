#!/bin/bash

# EC2에서 Nginx 설정 확인 및 수정

echo "=== Nginx 설정 확인 및 수정 ==="
echo ""
echo "EC2에서 다음 명령어를 순서대로 실행하세요:"
echo ""

cat << 'EOF'
# 1. 현재 sites-enabled 확인
echo "=== 현재 활성화된 사이트 설정 ==="
ls -la /etc/nginx/sites-enabled/

# 2. 기본 설정 내용 확인
echo ""
echo "=== 기본 설정 내용 ==="
sudo cat /etc/nginx/sites-enabled/default | head -20

# 3. 포트 사용 확인
echo ""
echo "=== 80번 포트 사용 프로세스 ==="
sudo lsof -i :80

# 4. 8000번 포트 확인 (Docker 컨테이너)
echo ""
echo "=== 8000번 포트 사용 프로세스 ==="
sudo lsof -i :8000

# 5. Smart Yoram 설정 적용
echo ""
echo "=== Smart Yoram 프록시 설정 적용 ==="
cd ~/smart-yoram/smart-yoram-backend

# nginx-simple.conf 파일이 있는지 확인
if [ -f deploy/nginx-simple.conf ]; then
    # 설정 파일 복사
    sudo cp deploy/nginx-simple.conf /etc/nginx/sites-available/smartyoram
    
    # 기존 default 비활성화
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # smartyoram 활성화
    sudo ln -sf /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/
    
    # 설정 테스트
    echo ""
    echo "=== Nginx 설정 테스트 ==="
    sudo nginx -t
    
    # Nginx 리로드
    echo ""
    echo "=== Nginx 리로드 ==="
    sudo systemctl reload nginx
    
    # 상태 확인
    echo ""
    echo "=== Nginx 상태 ==="
    sudo systemctl status nginx --no-pager
    
    # 테스트
    echo ""
    echo "=== 로컬 테스트 ==="
    curl -I http://localhost
    
    echo ""
    echo "=== 완료! ==="
    echo "브라우저에서 접속: http://$(curl -s ifconfig.me)"
    echo "API 문서: http://$(curl -s ifconfig.me)/docs"
else
    echo "ERROR: nginx-simple.conf 파일을 찾을 수 없습니다!"
    echo "git pull로 최신 코드를 받아주세요."
fi
EOF