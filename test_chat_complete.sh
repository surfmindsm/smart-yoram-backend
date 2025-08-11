#!/bin/bash

echo "Testing Chat API with initialized data"
echo "======================================"
echo ""

# Server URL
BASE_URL="https://api.surfmind-team.com/api/v1"

# Test with the current token
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTU0OTE2NTIsInN1YiI6IjE0In0.yv2kerjcFy5kP5H5OxuzCBFXAZ14WCEr9QTMJV2s02M"

echo "1. Testing with agent_id=1, chat_history_id=2"
echo "----------------------------------------------"

curl -X POST "${BASE_URL}/chat/messages" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_history_id": "2",
    "agent_id": "1",
    "content": "안녕하세요! 오늘 날씨가 어떤가요?"
  }' | python3 -m json.tool

echo ""
echo "Test completed!"