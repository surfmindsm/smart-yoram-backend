#!/bin/bash

# CloudFlared를 데몬으로 실행하는 스크립트

echo "=== CloudFlared 데몬 설정 ==="
echo ""

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 기존 cloudflared 프로세스 종료
echo -e "${BLUE}1. 기존 cloudflared 프로세스 확인 및 종료...${NC}"
if pgrep -f cloudflared > /dev/null; then
    echo "기존 프로세스 발견, 종료 중..."
    pkill -f cloudflared
    sleep 2
fi

# 2. 로그 디렉토리 생성
echo -e "${BLUE}2. 로그 디렉토리 생성...${NC}"
mkdir -p ~/logs

# 3. CloudFlared 데몬 시작
echo -e "${BLUE}3. CloudFlared 데몬 시작...${NC}"
nohup cloudflared tunnel --url http://localhost:8000 > ~/logs/cloudflared.log 2>&1 &

# 프로세스 ID 저장
echo $! > ~/cloudflared.pid
echo -e "${GREEN}✓ CloudFlared PID: $(cat ~/cloudflared.pid)${NC}"

# 4. URL 확인 (10초 대기)
echo -e "${BLUE}4. Tunnel URL 확인 중...${NC}"
sleep 10

# URL 추출
TUNNEL_URL=$(grep -o 'https://.*\.trycloudflare\.com' ~/logs/cloudflared.log | tail -1)

if [ -n "$TUNNEL_URL" ]; then
    echo -e "${GREEN}✓ Tunnel URL: $TUNNEL_URL${NC}"
    echo ""
    echo -e "${YELLOW}=== 다음 단계 ===${NC}"
    echo "1. 프론트엔드 .env.production 업데이트:"
    echo "   REACT_APP_API_URL=$TUNNEL_URL/api/v1"
    echo ""
    echo "2. EC2 백엔드 .env의 CORS에 추가:"
    echo "   \"$TUNNEL_URL\""
else
    echo -e "${RED}✗ URL을 찾을 수 없습니다. 로그 확인:${NC}"
    echo "   tail -f ~/logs/cloudflared.log"
fi

echo ""
echo -e "${BLUE}=== 유용한 명령어 ===${NC}"
echo "로그 확인: tail -f ~/logs/cloudflared.log"
echo "프로세스 확인: ps aux | grep cloudflared"
echo "프로세스 종료: kill \$(cat ~/cloudflared.pid)"
echo "URL 다시 확인: grep 'trycloudflare.com' ~/logs/cloudflared.log | tail -1"