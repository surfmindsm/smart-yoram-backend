#!/bin/bash
# Script to fix BACKEND_CORS_ORIGINS format in .env file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Fixing BACKEND_CORS_ORIGINS in .env file...${NC}"

if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    exit 1
fi

# Backup current .env
cp .env .env.backup
echo -e "${YELLOW}Backup created: .env.backup${NC}"

# Fix smart quotes to regular quotes
sed -i "s/[""]/\"/g" .env
sed -i "s/['']/'/g" .env

# Alternative fix: Convert BACKEND_CORS_ORIGINS to simple comma-separated format
# Uncomment the following line if JSON array format continues to cause issues:
# sed -i 's/BACKEND_CORS_ORIGINS=\[.*\]/BACKEND_CORS_ORIGINS=http:\/\/localhost:3000,http:\/\/localhost:8080,https:\/\/smart-yoram-admin.vercel.app/' .env

echo -e "${GREEN}✅ Fixed quote formatting in .env file${NC}"

# Test if Python can parse the config
echo -e "${YELLOW}Testing configuration...${NC}"
python3 -c "
import json
import re

with open('.env', 'r') as f:
    for line in f:
        if line.startswith('BACKEND_CORS_ORIGINS='):
            value = line.split('=', 1)[1].strip()
            if value.startswith('['):
                try:
                    origins = json.loads(value)
                    print('✅ BACKEND_CORS_ORIGINS is valid JSON:', origins[:2], '...')
                except json.JSONDecodeError as e:
                    print('❌ JSON parsing error:', e)
                    print('Value:', value[:100])
            else:
                origins = [o.strip() for o in value.split(',')]
                print('✅ BACKEND_CORS_ORIGINS as comma-separated:', origins[:2], '...')
            break
" || echo -e "${YELLOW}Could not test configuration with Python${NC}"

echo -e "${GREEN}Done! Now restart the application:${NC}"
echo "  docker-compose restart"
echo "  # or"
echo "  docker-compose down && docker-compose up -d"