#!/bin/bash

# EC2로 SSH 키를 복사하는 스크립트

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Copy SSH Keys to EC2 ===${NC}"
echo ""

# 변수 설정
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./copy-ssh-to-ec2.sh <EC2_IP> <PEM_FILE>"
    echo "Example: ./copy-ssh-to-ec2.sh 13.125.xxx.xxx ~/keys/my-key.pem"
    exit 1
fi

EC2_IP=$1
PEM_FILE=$2

# PEM 파일 확인
if [ ! -f "$PEM_FILE" ]; then
    echo -e "${RED}Error: PEM file not found: $PEM_FILE${NC}"
    exit 1
fi

# SSH 키 확인
if [ ! -f ~/.ssh/surfmind_github ]; then
    echo -e "${RED}Error: SSH key not found: ~/.ssh/surfmind_github${NC}"
    echo "Please run setup_git_ssh.sh first"
    exit 1
fi

echo -e "${BLUE}1. Copying SSH keys to EC2...${NC}"
scp -i "$PEM_FILE" ~/.ssh/surfmind_github ubuntu@$EC2_IP:~/
scp -i "$PEM_FILE" ~/.ssh/surfmind_github.pub ubuntu@$EC2_IP:~/

echo -e "${BLUE}2. Setting up SSH on EC2...${NC}"
ssh -i "$PEM_FILE" ubuntu@$EC2_IP << 'ENDSSH'
# SSH 디렉토리 설정
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# SSH 키 이동 및 권한 설정
mv ~/surfmind_github ~/.ssh/
mv ~/surfmind_github.pub ~/.ssh/
chmod 600 ~/.ssh/surfmind_github
chmod 644 ~/.ssh/surfmind_github.pub

# SSH config 설정
cat > ~/.ssh/config << 'EOF'
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/surfmind_github
    IdentitiesOnly yes
    StrictHostKeyChecking no
EOF
chmod 600 ~/.ssh/config

# Git 설정
git config --global user.name "Surfmind"
git config --global user.email "surfmind.sm@gmail.com"

echo "SSH setup completed!"
ENDSSH

echo -e "${BLUE}3. Testing SSH connection...${NC}"
ssh -i "$PEM_FILE" ubuntu@$EC2_IP "ssh -T git@github.com 2>&1 | cat"

echo ""
echo -e "${GREEN}✓ SSH keys copied and configured!${NC}"
echo ""
echo "Now you can SSH into EC2 and clone with:"
echo -e "${YELLOW}git clone git@github.com:surfmindsm/smart-yoram-backend.git${NC}"