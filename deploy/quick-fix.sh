#!/bin/bash

echo "Quick fix for deployment issues..."

cd ~/smart-yoram/smart-yoram-backend

# Fix import in health.py
sed -i 's/from app.core.redis import get_redis_client/from app.core.redis import redis_client/' app/api/api_v1/endpoints/health.py
sed -i '/redis_client = get_redis_client()/d' app/api/api_v1/endpoints/health.py

# Rebuild
docker-compose build backend

# Restart all services
docker-compose down
docker-compose up -d

echo "Fix completed. Checking logs..."
sleep 5
docker logs smart-yoram-backend_backend_1 --tail 30