#!/bin/bash
# Script to encode .env file to base64 for GitHub Environment Variables

if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please create .env file first"
    exit 1
fi

echo "Encoding .env file to base64..."
echo ""
echo "Copy the following base64 string to GitHub Environment Variable (ENV_FILE_BASE64):"
echo "========================================="
base64 -w 0 .env 2>/dev/null || base64 .env | tr -d '\n'
echo ""
echo "========================================="
echo ""
echo "This encoded string preserves all line breaks and special characters."