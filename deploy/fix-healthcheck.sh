#!/bin/bash

# Docker 헬스체크 문제 해결 스크립트

echo "=== Docker 헬스체크 수정 ==="
echo ""
echo "EC2에서 다음 명령어를 실행하세요:"
echo ""

cat << 'EOF'
# 1. 최신 코드 받기
cd ~/smart-yoram/smart-yoram-backend
git pull origin main

# 2. Docker 컨테이너 재빌드
echo "Docker 컨테이너 재빌드 중..."
docker-compose down
docker-compose up -d --build

# 3. 빌드 완료 대기 (약 1-2분)
echo "빌드 완료 대기 중..."
sleep 30

# 4. 컨테이너 상태 확인
echo ""
echo "컨테이너 상태:"
docker-compose ps

# 5. 헬스체크 확인
echo ""
echo "헬스체크 테스트:"
docker-compose exec backend curl -f http://localhost:8000/ && echo "✓ 헬스체크 성공!" || echo "✗ 헬스체크 실패"

# 6. 로그 확인
echo ""
echo "최근 로그:"
docker-compose logs --tail=20 backend

# 7. 외부 접속 테스트
echo ""
echo "외부 접속 테스트:"
curl -I http://localhost:8000

echo ""
echo "=== 완료! ==="
echo "이제 헬스체크가 정상 작동해야 합니다."
echo "브라우저에서 확인: http://$(curl -s ifconfig.me):8000"
EOF

echo ""
echo "참고: Dockerfile에 curl을 추가하여 헬스체크가 작동하도록 수정했습니다."