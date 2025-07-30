#!/bin/bash

# EC2에서 .env 파일 생성 스크립트

echo "=== .env 파일 생성 ==="
echo ""
echo "EC2에서 이 내용을 복사하여 .env 파일을 만드세요:"
echo ""

cat << 'EOF'
# .env 파일 백업
cp .env .env.backup.$(date +%Y%m%d-%H%M%S)

# 새 .env 파일 생성
cat > .env << 'ENVFILE'
# Database (Supabase)
# Pooler connection (us-east-2)
DATABASE_URL=postgresql://postgres.adzhdsajdamrflvybhxq:7Vhg9aJh5rv76zI7@aws-0-us-east-2.pooler.supabase.com:6543/postgres

# Supabase
SUPABASE_URL=https://adzhdsajdamrflvybhxq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkemhkc2FqZGFtcmZsdnliaHhxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM4NDg5ODEsImV4cCI6MjA2OTQyNDk4MX0.pgn6M5_ihDFt3ojQmCoc3Qf8pc7LzRvQEIDT7g1nW3c

# Security
SECRET_KEY=smart-yoram-secret-key-2025-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "https://smart-yoram-admin.vercel.app", "https://lloyd-kuwait-margaret-territory.trycloudflare.com"]

# Application
PROJECT_NAME="Smart Yoram API"
VERSION="1.0.0"
API_V1_STR="/api/v1"
ENVFILE

echo ".env 파일이 생성되었습니다."
cat .env
EOF