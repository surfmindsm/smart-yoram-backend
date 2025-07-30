#!/bin/bash

# EC2 Ubuntu 22.04 LTS 설정 스크립트

echo "=== Smart Yoram Backend EC2 Setup ==="

# 1. 시스템 업데이트
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# 2. 필수 패키지 설치
echo "2. Installing required packages..."
sudo apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    htop \
    ufw

# 3. Docker 권한 설정
echo "3. Setting up Docker permissions..."
sudo usermod -aG docker $USER
sudo systemctl enable docker
sudo systemctl start docker

# 4. 방화벽 설정
echo "4. Configuring firewall..."
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000/tcp  # Backend (개발용, 프로덕션에서는 제거)
sudo ufw --force enable

# 5. 프로젝트 디렉토리 생성
echo "5. Creating project directory..."
mkdir -p ~/smart-yoram
cd ~/smart-yoram

# 6. 환경 변수 파일 생성
echo "6. Creating environment file..."
cat > .env << 'EOF'
# Database (Supabase)
DATABASE_URL=postgresql://postgres.adzhdsajdamrflvybhxq:7Vhg9aJh5rv76zI7@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://adzhdsajdamrflvybhxq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkemhkc2FqZGFtcmZsdnliaHhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NDg5ODEsImV4cCI6MjA2OTQyNDk4MX0.pgn6M5_ihDFt3ojQmCoc3Qf8pc7LzRvQEIDT7g1nW3c

# Security
SECRET_KEY=smart-yoram-secret-key-2025-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS - Update with your domain
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-frontend-domain.com"]
EOF

echo "7. Setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repository:"
echo "   git clone https://github.com/your-repo/smart-yoram-backend.git"
echo ""
echo "2. Build and run with Docker:"
echo "   cd smart-yoram-backend"
echo "   docker-compose up -d --build"
echo ""
echo "3. Set up SSL certificate (replace your-domain.com):"
echo "   sudo certbot --nginx -d your-domain.com"
echo ""
echo "4. Copy nginx configuration:"
echo "   sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartyoram"
echo "   sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"
echo ""
echo "5. Check logs:"
echo "   docker-compose logs -f"