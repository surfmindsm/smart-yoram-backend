#!/bin/bash

# EC2 서버에서 .env 파일의 BACKEND_CORS_ORIGINS 형식을 수정하는 스크립트

set -e

EC2_HOST="13.211.169.169"
EC2_USER="ubuntu"

echo "🔧 Fixing BACKEND_CORS_ORIGINS format on EC2 server..."

# SSH key 파일 경로 (필요시 수정)
SSH_KEY_PATH="~/.ssh/your-key.pem"

# SSH 명령어 생성 함수
ssh_ec2() {
    ssh -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$@"
}

# EC2에서 직접 수정
ssh_ec2 << 'ENDSSH'
cd ~/smart-yoram-backend

echo "📝 Current BACKEND_CORS_ORIGINS value:"
grep BACKEND_CORS_ORIGINS .env || echo "Not found"

echo ""
echo "🔧 Fixing BACKEND_CORS_ORIGINS format..."

# Python 스크립트로 수정
python3 << 'ENDPYTHON'
import os

# Read .env file
with open('.env', 'r') as f:
    lines = f.readlines()

# Fix BACKEND_CORS_ORIGINS line
new_lines = []
for line in lines:
    if line.startswith('BACKEND_CORS_ORIGINS='):
        # Use simple comma-separated format instead of JSON array
        new_lines.append('BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8080,https://smart-yoram-admin.vercel.app\n')
        print(f"Fixed: {line.strip()} -> comma-separated format")
    else:
        new_lines.append(line)

# Write back
with open('.env', 'w') as f:
    f.writelines(new_lines)

print("✅ .env file updated")
ENDPYTHON

echo ""
echo "📝 New BACKEND_CORS_ORIGINS value:"
grep BACKEND_CORS_ORIGINS .env

echo ""
echo "🔄 Restarting Docker containers..."
sudo docker-compose down
sudo docker-compose up -d --force-recreate

echo ""
echo "⏳ Waiting for containers to start..."
sleep 10

echo ""
echo "📊 Container status:"
sudo docker-compose ps

echo ""
echo "📋 Backend logs (last 20 lines):"
sudo docker-compose logs --tail=20 backend

echo ""
echo "🧪 Testing health endpoint:"
curl -f http://localhost:8000/health || echo "Health check failed"

ENDSSH

echo "✅ Done!"