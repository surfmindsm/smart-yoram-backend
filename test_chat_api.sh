#!/bin/bash

# Get token first
echo "Getting authentication token..."
TOKEN_RESPONSE=$(curl -s -X POST "https://api.surfmind-team.com/api/v1/auth/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sungkwang21.org&password=admin123!")

TOKEN=$(echo $TOKEN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ]; then
    echo "Failed to get token"
    exit 1
fi

echo "Token obtained successfully"
echo ""

# Test chat message endpoint
echo "Testing chat message endpoint..."
curl -X POST "https://api.surfmind-team.com/api/v1/chat/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_history_id": 1,
    "agent_id": 1,
    "content": "안녕하세요! 오늘 날씨가 어떤가요?"
  }' | python3 -m json.tool

echo ""
echo "Test completed"