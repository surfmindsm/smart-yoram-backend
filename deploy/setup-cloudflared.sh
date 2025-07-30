#!/bin/bash

# CloudFlare Tunnel 설정 스크립트

echo "=== CloudFlare Tunnel 설정 가이드 ==="
echo ""

cat << 'EOF'
# 1. CloudFlared 설치
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
sudo mv cloudflared /usr/local/bin/

# 2. CloudFlare Tunnel 시작 (백그라운드)
# 옵션 A: 임시 URL (매번 변경됨)
nohup cloudflared tunnel --url http://localhost:80 > cloudflared.log 2>&1 &

# 3. URL 확인
sleep 5
grep "trycloudflare.com" cloudflared.log

# 4. 영구적인 URL을 원한다면 CloudFlare Zero Trust 사용
# https://one.dash.cloudflare.com/

# 5. 또는 ngrok 사용 (대안)
# ngrok은 무료로 고정 도메인 제공
# https://ngrok.com/
EOF

echo ""
echo "=== 대안: 직접 IP 사용 (개발용) ==="
echo ""
echo "1. Vercel에서 Mixed Content 허용 (Chrome):"
echo "   - 주소창 자물쇠 클릭 → Site settings → Insecure content → Allow"
echo ""
echo "2. 또는 HTTP로 로컬 테스트:"
echo "   - npm run build"
echo "   - serve -s build"
echo "   - http://localhost:3000 에서 테스트"