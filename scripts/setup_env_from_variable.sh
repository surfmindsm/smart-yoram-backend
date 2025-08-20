#!/bin/bash
# Setup script to create .env file from single environment variable

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Smart Yoram Backend environment...${NC}"

# Check if ENV_FILE variable is set
if [ -z "$ENV_FILE" ]; then
    echo -e "${RED}ERROR: ENV_FILE environment variable is not set!${NC}"
    echo "Please set ENV_FILE variable with the complete .env file content"
    exit 1
fi

# Create .env file from ENV_FILE variable
echo -e "${YELLOW}Creating .env file from ENV_FILE variable...${NC}"
echo "$ENV_FILE" > .env

# Set proper permissions
chmod 600 .env
echo -e "${GREEN}✅ .env file created successfully!${NC}"

# Create app.log if it doesn't exist
touch app.log
chmod 666 app.log

# Show first few lines of .env (without sensitive data)
echo -e "${YELLOW}Environment file created with $(wc -l < .env) lines${NC}"
echo -e "${GREEN}✅ Environment setup complete!${NC}"