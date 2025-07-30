#!/bin/bash

# CloudFlared를 systemd 서비스로 설정하는 스크립트

echo "=== CloudFlared Systemd 서비스 설정 ==="
echo ""

# 서비스 파일 생성
sudo tee /etc/systemd/system/cloudflared.service > /dev/null << 'EOF'
[Unit]
Description=CloudFlare Tunnel
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu
ExecStart=/usr/local/bin/cloudflared tunnel --url http://localhost:8000
Restart=always
RestartSec=10
StandardOutput=append:/home/ubuntu/logs/cloudflared.log
StandardError=append:/home/ubuntu/logs/cloudflared.error.log

[Install]
WantedBy=multi-user.target
EOF

echo "1. 서비스 파일 생성 완료"

# 로그 디렉토리 생성
mkdir -p ~/logs

# systemd 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

echo "2. 서비스 시작 및 자동 시작 설정 완료"

# 상태 확인
echo ""
echo "3. 서비스 상태:"
sudo systemctl status cloudflared --no-pager

# URL 확인
echo ""
echo "4. Tunnel URL 확인 중 (10초 대기)..."
sleep 10

TUNNEL_URL=$(grep -o 'https://.*\.trycloudflare\.com' ~/logs/cloudflared.log | tail -1)
if [ -n "$TUNNEL_URL" ]; then
    echo ""
    echo "=== ✓ CloudFlared 서비스 설정 완료 ==="
    echo "Tunnel URL: $TUNNEL_URL"
    echo ""
    echo "서비스 관리 명령어:"
    echo "- 상태 확인: sudo systemctl status cloudflared"
    echo "- 재시작: sudo systemctl restart cloudflared"
    echo "- 중지: sudo systemctl stop cloudflared"
    echo "- 로그 확인: tail -f ~/logs/cloudflared.log"
else
    echo "URL을 아직 찾을 수 없습니다. 로그를 확인하세요:"
    echo "tail -f ~/logs/cloudflared.log"
fi