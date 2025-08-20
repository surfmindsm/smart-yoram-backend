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
# Try different base64 commands for different OS
if command -v base64 >/dev/null 2>&1; then
    if base64 --help 2>&1 | grep -q -- '-w'; then
        # Linux with -w option
        base64 -w 0 .env
    elif base64 --help 2>&1 | grep -q -- '-i'; then
        # macOS with -i option
        base64 -i .env | tr -d '\n'
    else
        # Fallback
        base64 < .env | tr -d '\n'
    fi
else
    echo "Error: base64 command not found!"
    exit 1
fi
echo ""
echo "========================================="
echo ""
echo "This encoded string preserves all line breaks and special characters."