#!/bin/bash
# Deploy Smart Yoram Backend to EC2

echo "🚀 Deploying Smart Yoram Backend to EC2..."

# SSH to EC2 and update the code
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip << 'EOF'
cd /home/ubuntu/smart-yoram-backend

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Restart the application
echo "🔄 Restarting application..."
sudo systemctl restart smart-yoram
sudo systemctl restart nginx

echo "✅ Deployment complete!"
EOF

echo "✅ Deployment script completed!"