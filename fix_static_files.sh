#!/bin/bash

# Fix static files serving for Smart Yoram Backend
echo "🔧 Static Files 404 해결 스크립트"

# 1. Get current working directory
BACKEND_PATH=$(pwd)
echo "📁 Backend 경로: $BACKEND_PATH"

# 2. Create static directories if they don't exist
echo "📂 Static 디렉토리 생성 중..."
mkdir -p static/community/images
chmod 755 static
chmod 755 static/community
chmod 755 static/community/images

# 3. Update nginx configuration with correct path
echo "⚙️  nginx 설정 업데이트 중..."
sed -i.bak "s|/path/to/your/backend/static/|$BACKEND_PATH/static/|g" nginx.conf

# 4. Check if specific image exists
IMAGE_FILE="community_9998_20250910_143039_41925038.png"
if [ ! -f "static/community/images/$IMAGE_FILE" ]; then
    echo "❌ 이미지 파일 없음: static/community/images/$IMAGE_FILE"
    echo "   이 파일이 실제로 업로드되었는지 확인이 필요합니다."
else
    echo "✅ 이미지 파일 존재: static/community/images/$IMAGE_FILE"
fi

# 5. Display current static files
echo "📋 현재 static 파일 목록:"
find static/ -type f 2>/dev/null || echo "   (static 파일 없음)"

# 6. Test nginx configuration
echo "🧪 nginx 설정 테스트..."
if command -v nginx >/dev/null 2>&1; then
    nginx -t -c $BACKEND_PATH/nginx.conf
    if [ $? -eq 0 ]; then
        echo "✅ nginx 설정이 유효합니다."
        echo "🔄 nginx 재시작을 위해 다음 명령어를 실행하세요:"
        echo "   sudo systemctl reload nginx"
        echo "   또는"
        echo "   sudo nginx -s reload"
    else
        echo "❌ nginx 설정에 오류가 있습니다."
    fi
else
    echo "⚠️  nginx가 설치되지 않았거나 PATH에 없습니다."
fi

# 7. Provide additional troubleshooting info
echo ""
echo "🔍 추가 확인 사항:"
echo "1. 서버의 실제 backend 경로가 맞는지 확인"
echo "2. static 디렉토리 권한이 nginx 사용자가 읽을 수 있는지 확인"
echo "3. 업로드된 이미지 파일이 실제로 존재하는지 확인"
echo ""
echo "🌐 업데이트된 nginx 설정에서 static 파일 경로:"
echo "   $BACKEND_PATH/static/"