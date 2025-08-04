#!/bin/bash

echo "Fixing deployment issues on EC2..."

# Fix import in health.py
echo "1. Fixing import in health.py..."
sed -i 's/from app.db.session import get_db/from app.api.deps import get_db/' app/api/api_v1/endpoints/health.py

# Create proper firebase-credentials.json file
echo "2. Creating empty firebase-credentials.json..."
rm -rf firebase-credentials.json
touch firebase-credentials.json

# Rebuild and restart
echo "3. Rebuilding and restarting containers..."
docker-compose down
docker-compose build backend
docker-compose up -d

echo "4. Waiting for services to start..."
sleep 10

# Check status
echo "5. Checking service status..."
docker-compose ps
echo ""
echo "Latest logs:"
docker logs smart-yoram-backend_backend_1 --tail 50

echo "Deployment fix completed!"