#!/bin/bash

# Smart Yoram Backend - EC2 빠른 배포 스크립트
# EC2 인스턴스에서 실행

set -e  # 에러 발생시 중단

echo "=== Smart Yoram Backend EC2 Quick Deploy ==="

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. 기본 패키지 업데이트
echo -e "${BLUE}1. Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Docker 설치 확인
echo -e "${BLUE}2. Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${YELLOW}Please logout and login again for docker permissions${NC}"
fi

# 3. Docker Compose 설치 확인
echo -e "${BLUE}3. Checking Docker Compose installation...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt install -y docker-compose
fi

# 4. Nginx 설치
echo -e "${BLUE}4. Installing Nginx...${NC}"
sudo apt install -y nginx

# 5. Git 설치 및 설정
echo -e "${BLUE}5. Setting up Git...${NC}"
sudo apt install -y git
git config --global user.name "Surfmind"
git config --global user.email "surfmind.sm@gmail.com"

# 6. 프로젝트 클론
echo -e "${BLUE}6. Cloning project...${NC}"
cd ~
if [ ! -d "smart-yoram" ]; then
    mkdir smart-yoram
fi
cd smart-yoram

if [ ! -d "smart-yoram-backend" ]; then
    # SSH 키가 있는지 확인
    if [ -f ~/.ssh/surfmind_github ] || [ -f ~/.ssh/deploy_key ]; then
        echo "Using SSH to clone..."
        git clone git@github.com:surfmindsm/smart-yoram-backend.git
    else
        echo "Using HTTPS to clone (public repository only)..."
        git clone https://github.com/surfmindsm/smart-yoram-backend.git
        echo -e "${YELLOW}Note: For private repositories, setup SSH keys first${NC}"
    fi
fi
cd smart-yoram-backend

# 7. 환경 변수 설정
echo -e "${BLUE}7. Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration:${NC}"
    echo "nano .env"
    echo ""
    echo "Required changes:"
    echo "1. Update SECRET_KEY"
    echo "2. Update BACKEND_CORS_ORIGINS with your frontend domain"
    echo ""
    read -p "Press enter after editing .env file..."
fi

# 8. Docker 실행
echo -e "${BLUE}8. Starting Docker containers...${NC}"
docker-compose down
docker-compose up -d --build

# 9. 헬스체크
echo -e "${BLUE}9. Health check...${NC}"
sleep 10
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running!${NC}"
else
    echo -e "${RED}✗ Backend health check failed!${NC}"
    docker-compose logs --tail=50
fi

# 10. Nginx 설정 정보
echo -e "${BLUE}10. Nginx setup instructions:${NC}"
echo "To setup Nginx (if you have a domain):"
echo "1. sudo cp deploy/nginx.conf /etc/nginx/sites-available/smartyoram"
echo "2. Edit the file and replace 'your-domain.com' with your actual domain"
echo "3. sudo ln -s /etc/nginx/sites-available/smartyoram /etc/nginx/sites-enabled/"
echo "4. sudo rm /etc/nginx/sites-enabled/default"
echo "5. sudo nginx -t"
echo "6. sudo systemctl reload nginx"

echo ""
echo -e "${GREEN}=== Deployment Complete! ===${NC}"
echo ""
echo "Access your API at:"
echo "- http://$(curl -s ifconfig.me):8000"
echo "- http://$(curl -s ifconfig.me):8000/docs"
echo ""
echo "Next steps:"
echo "1. Configure Nginx for your domain"
echo "2. Setup SSL with: sudo certbot --nginx -d your-domain.com"
echo "3. Remove port 8000 from security group for production"