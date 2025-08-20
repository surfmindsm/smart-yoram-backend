#!/bin/bash
# Setup script for EC2 environment variables from GitHub Secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Smart Yoram Backend environment from GitHub Secrets...${NC}"

# These environment variables should be passed from GitHub Actions
# Check if all required variables are set
required_vars=(
    "DATABASE_URL"
    "SUPABASE_URL" 
    "SUPABASE_ANON_KEY"
    "SECRET_KEY"
    "BACKEND_CORS_ORIGINS"
)

missing_vars=()
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "${RED}ERROR: Missing required environment variables:${NC}"
    printf '%s\n' "${missing_vars[@]}"
    exit 1
fi

# Create .env file from environment variables
echo -e "${YELLOW}Creating .env file from environment variables...${NC}"

cat > .env << EOF
# Database (Supabase)
DATABASE_URL=${DATABASE_URL}

# Supabase
SUPABASE_URL=${SUPABASE_URL}
SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

# Security
SECRET_KEY=${SECRET_KEY}
ALGORITHM=${ALGORITHM:-HS256}
ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES:-10080}

# CORS
BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}

# OpenAI API (Optional)
OPENAI_API_KEY=${OPENAI_API_KEY:-}
OPENAI_ORGANIZATION=${OPENAI_ORGANIZATION:-}

# API Keys
API_KEYS=${API_KEYS:-}

# Application
PROJECT_NAME="${PROJECT_NAME:-Smart Yoram API}"
VERSION="${VERSION:-1.0.0}"
API_V1_STR="${API_V1_STR:-/api/v1}"

# Redis (Optional)
REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}

# Firebase (Optional)
FIREBASE_CREDENTIALS_PATH=${FIREBASE_CREDENTIALS_PATH:-firebase-credentials.json}

# Admin User
FIRST_SUPERUSER=${FIRST_SUPERUSER:-admin@smartyoram.com}
FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD:-changeme}
EOF

# Set proper permissions
chmod 600 .env
echo -e "${GREEN}✅ .env file created successfully!${NC}"

# Create app.log if it doesn't exist
touch app.log
chmod 666 app.log

echo -e "${GREEN}✅ Environment setup complete!${NC}"