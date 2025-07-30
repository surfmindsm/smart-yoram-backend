#!/bin/bash

# EC2에서 Nginx 설정을 직접 실행하는 스크립트

echo "=== Nginx 프록시 설정 시작 ==="

# 1. 현재 sites-enabled 확인
echo ""
echo "1. 현재 활성화된 사이트 설정:"
ls -la /etc/nginx/sites-enabled/

# 2. nginx-simple.conf 파일 확인
if [ ! -f deploy/nginx-simple.conf ]; then
    echo "ERROR: nginx-simple.conf 파일을 찾을 수 없습니다!"
    echo "git pull로 최신 코드를 받아주세요:"
    echo "git pull origin main"
    exit 1
fi

# 3. Smart Yoram 설정 적용
echo ""
echo "2. Smart Yoram 프록시 설정 적용중..."

# 설정 파일 복사
sudo cp deploy/nginx-simple.conf /etc/nginx/sites-available/smartyoram

# 기존 default 비활성화
sudo rm -f /etc/nginx/sites-enabled/default

# smartyoram 활성화
sudo ln -sf /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/

# 4. 설정 테스트
echo ""
echo "3. Nginx 설정 테스트:"
sudo nginx -t

if [ $? -ne 0 ]; then
    echo "ERROR: Nginx 설정에 문제가 있습니다!"
    exit 1
fi

# 5. Nginx 리로드
echo ""
echo "4. Nginx 리로드:"
sudo systemctl reload nginx

# 6. 상태 확인
echo ""
echo "5. Nginx 상태:"
sudo systemctl status nginx --no-pager | head -10

# 7. 포트 확인
echo ""
echo "6. 포트 사용 현황:"
echo "80번 포트:"
sudo lsof -i :80 | head -5
echo ""
echo "8000번 포트:"
sudo lsof -i :8000 | head -5

# 8. 테스트
echo ""
echo "7. 연결 테스트:"
curl -I http://localhost 2>/dev/null | head -5

# 9. 외부 IP 확인
EXTERNAL_IP=$(curl -s ifconfig.me)

echo ""
echo "=== ✅ 설정 완료! ==="
echo ""
echo "접속 주소:"
echo "- API: http://$EXTERNAL_IP"
echo "- API 문서: http://$EXTERNAL_IP/docs"
echo ""
echo "만약 접속이 안 되면:"
echo "1. EC2 Security Group에서 80번 포트가 열려있는지 확인"
echo "2. Docker 컨테이너가 실행 중인지 확인: docker-compose ps"