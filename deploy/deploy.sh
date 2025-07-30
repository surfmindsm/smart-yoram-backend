#!/bin/bash

# 배포 스크립트

echo "=== Smart Yoram Backend Deployment ==="

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Git pull
echo -e "${GREEN}1. Pulling latest changes...${NC}"
git pull origin main

# 2. Docker 이미지 빌드 및 실행
echo -e "${GREEN}2. Building and starting Docker containers...${NC}"
docker-compose down
docker-compose up -d --build

# 3. 헬스체크
echo -e "${GREEN}3. Waiting for health check...${NC}"
sleep 10

# 헬스체크 확인
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running successfully!${NC}"
else
    echo -e "${RED}✗ Backend health check failed!${NC}"
    echo "Checking logs..."
    docker-compose logs --tail=50
    exit 1
fi

# 4. 컨테이너 상태 확인
echo -e "${GREEN}4. Container status:${NC}"
docker-compose ps

echo -e "${GREEN}Deployment completed successfully!${NC}"