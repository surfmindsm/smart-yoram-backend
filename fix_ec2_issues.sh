#!/bin/bash
# Fix EC2 deployment issues for Smart Yoram Backend

echo "🔧 Fixing EC2 deployment issues..."

# Navigate to project directory
cd /home/ubuntu/smart-yoram/smart-yoram-backend

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Rebuild Docker image
echo "🐳 Rebuilding Docker image..."
docker-compose build

# Restart containers
echo "🔄 Restarting containers..."
docker-compose down
docker-compose up -d

# Check logs
echo "📋 Checking logs..."
docker-compose logs --tail=50

echo "✅ Done! The static directory issue should be fixed."
echo ""
echo "⚠️  IMPORTANT: You still need to manually create Supabase Storage buckets:"
echo "   1. Go to https://app.supabase.com"
echo "   2. Navigate to Storage section"
echo "   3. Create these buckets:"
echo "      - member-photos"
echo "      - bulletins"
echo "      - documents"
echo ""
echo "📝 See SUPABASE_STORAGE_SETUP.md for detailed instructions."