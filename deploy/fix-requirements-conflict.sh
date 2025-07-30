#!/bin/bash

# Fix requirements.txt pydantic version conflict for EC2 deployment

echo "=== Fixing Requirements Conflict ==="
echo ""
echo "Run this on EC2 after pulling the latest changes:"
echo ""

cat << 'EOF'
# 1. Pull latest changes
cd ~/smart-yoram/smart-yoram-backend
git pull origin main

# 2. Rebuild Docker containers
docker-compose down
docker-compose up -d --build

# 3. Check logs
docker-compose logs -f backend
EOF

echo ""
echo "The requirements.txt has been updated to use flexible version constraints:"
echo "- pydantic>=2.10.4,<3.0.0"
echo "- pydantic-settings>=2.6.1,<3.0.0"
echo ""
echo "This allows pip to resolve compatible versions automatically."