#!/bin/bash
# Check the actual error from the photo upload endpoint

echo "Testing photo upload endpoint..."
curl -X POST https://packs-holds-marc-extended.trycloudflare.com/api/v1/members/63/upload-photo \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.jpg" \
  -v