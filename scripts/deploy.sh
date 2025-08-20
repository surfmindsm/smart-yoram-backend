#!/bin/bash

# Smart Yoram Backend Deployment Script
# This script handles the deployment process on the EC2 instance

set -e  # Exit on error

echo "🚀 Starting Smart Yoram Backend Deployment..."

# Configuration
APP_DIR="/home/ubuntu/smart-yoram-backend"
LOG_DIR="/home/ubuntu/logs"
BACKUP_DIR="/home/ubuntu/backups"

# Create necessary directories
mkdir -p $LOG_DIR
mkdir -p $BACKUP_DIR

# Navigate to application directory
cd $APP_DIR

# Create backup of current deployment
if [ -d "$APP_DIR" ]; then
    echo "📦 Creating backup of current deployment..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    tar -czf "$BACKUP_DIR/backup_$timestamp.tar.gz" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        .
    
    # Keep only last 5 backups
    ls -t $BACKUP_DIR/backup_*.tar.gz | tail -n +6 | xargs -r rm
fi

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "📥 Pulling latest code from repository..."
    git pull origin main
fi

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# Update pip and install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
if [ -f ".env" ]; then
    source .env
fi
alembic upgrade head

# Collect static files if needed
# python manage.py collectstatic --noinput

# Deploy using Docker if docker-compose exists
if [ -f "docker-compose.yml" ]; then
    echo "🐳 Deploying with Docker Compose..."
    
    # Stop current containers
    docker-compose down
    
    # Build and start new containers
    docker-compose up -d --build
    
    # Wait for container to be healthy
    echo "⏳ Waiting for container to be healthy..."
    sleep 10
    
    # Check container status
    docker-compose ps
    
elif [ -f "/etc/systemd/system/smart-yoram-backend.service" ]; then
    echo "🔄 Restarting systemd service..."
    sudo systemctl daemon-reload
    sudo systemctl restart smart-yoram-backend
    sudo systemctl status smart-yoram-backend --no-pager
    
elif command -v supervisorctl &> /dev/null; then
    echo "🔄 Restarting supervisor service..."
    supervisorctl restart smart-yoram-backend
    supervisorctl status smart-yoram-backend
    
else
    echo "⚠️ No service manager configured. Starting application directly..."
    # Kill existing process
    pkill -f "uvicorn app.main:app" || true
    
    # Start application in background
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > $LOG_DIR/app.log 2>&1 &
    echo $! > $APP_DIR/app.pid
    echo "✅ Application started with PID: $(cat $APP_DIR/app.pid)"
fi

# Health check
echo "🏥 Performing health check..."
sleep 5

for i in {1..10}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Health check passed!"
        break
    else
        echo "⏳ Waiting for application to start... (attempt $i/10)"
        sleep 3
    fi
done

# Final status check
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "🎉 Deployment completed successfully!"
    echo "📊 Application is running at: http://localhost:8000"
else
    echo "❌ Deployment may have failed. Please check logs."
    exit 1
fi