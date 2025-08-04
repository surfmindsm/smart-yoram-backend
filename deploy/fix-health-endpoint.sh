#!/bin/bash

echo "Fixing health endpoint deployment issues..."

# SSH into EC2 and fix the issues
ssh -i ~/keys/smart-yoram.pem ubuntu@ec2-54-180-91-15.ap-northeast-2.compute.amazonaws.com << 'EOF'
cd ~/smart-yoram/smart-yoram-backend

# Fix the import path in health.py
echo "Fixing import path in health.py..."
docker exec smart-yoram-backend_backend_1 sed -i 's/from app.db.database import get_db/from app.db.session import get_db/' /app/app/api/v1/endpoints/health.py

# Fix Firebase credentials issue - remove the directory and touch an empty file
echo "Fixing Firebase credentials..."
docker exec smart-yoram-backend_backend_1 bash -c "rm -rf /app/firebase-credentials.json && touch /app/firebase-credentials.json"

# Restart the backend service
echo "Restarting backend service..."
docker-compose restart backend

echo "Waiting for service to start..."
sleep 10

# Check if service is running
docker-compose ps backend
docker logs smart-yoram-backend_backend_1 --tail 20

echo "Health endpoint fix completed!"
EOF