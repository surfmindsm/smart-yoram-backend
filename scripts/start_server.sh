#!/bin/bash
# Start script for Smart Yoram Backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Smart Yoram Backend...${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please copy .env.example to .env and update with your values:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if using Docker
if [ -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}Using Docker Compose...${NC}"
    
    # Stop any existing containers
    docker-compose down
    
    # Start containers
    docker-compose up -d --build
    
    echo -e "${GREEN}Docker containers started!${NC}"
    echo "Check logs with: docker-compose logs -f"
else
    echo -e "${YELLOW}Using Python virtual environment...${NC}"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install/update dependencies
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Run database migrations
    echo "Running database migrations..."
    alembic upgrade head || echo -e "${YELLOW}WARNING: Migration failed, continuing...${NC}"
    
    # Kill any existing process
    pkill -f "uvicorn app.main:app" || true
    
    # Start the application
    echo -e "${GREEN}Starting application on port 8000...${NC}"
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
    
    # Wait a moment
    sleep 3
    
    # Check if process is running
    if ps aux | grep "uvicorn app.main:app" | grep -v grep > /dev/null; then
        echo -e "${GREEN}✅ Application started successfully!${NC}"
        echo "Check logs with: tail -f app.log"
    else
        echo -e "${RED}❌ Failed to start application${NC}"
        echo "Check app.log for errors"
        exit 1
    fi
fi

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
sleep 2
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
    echo -e "${GREEN}Application is running at http://localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠️  Health check failed - application may still be starting${NC}"
fi