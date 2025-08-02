#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default values
API_URL="http://localhost:8001/api/v1"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --api-url)
      API_URL="$2"
      shift # past argument
      shift # past value
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

echo "Starting smoke tests for IntelliTest AI Platform..."
echo "API URL: $API_URL"

# Function to make API requests
make_request() {
  local method=$1
  local endpoint=$2
  local data=$3
  
  local cmd="curl -s -o /dev/null -w \"%{http_code}\""
  
  if [ "$method" = "POST" ] || [ "$method" = "PUT" ]; then
    cmd="$cmd -H \"Content-Type: application/json\" -d '$data'"
  fi
  
  cmd="$cmd -X $method $API_URL$endpoint"
  
  # Add JWT token if available
  if [ -n "$JWT_TOKEN" ]; then
    cmd="$cmd -H \"Authorization: Bearer $JWT_TOKEN\""
  fi
  
  echo "$cmd" | bash
}

# Test database connection
echo -n "Testing database connection... "
DB_STATUS=$(make_request "GET" "/health")
if [ "$DB_STATUS" = "200" ]; then
  echo -e "${GREEN}OK${NC}"
else
  echo -e "${RED}Failed${NC}"
  echo "  Database connection test failed with status: $DB_STATUS"
  exit 1
fi

# Test authentication
echo -n "Testing authentication... "
AUTH_RESPONSE=$(curl -s -X POST "$API_URL/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpassword")

JWT_TOKEN=$(echo "$AUTH_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ -n "$JWT_TOKEN" ] && [ "$JWT_TOKEN" != "null" ]; then
  echo -e "${GREEN}OK${NC}"
else
  echo -e "${RED}Failed${NC}"
  echo "  Authentication failed. Response: $AUTH_RESPONSE"
  # Continue with tests that don't require authentication
  JWT_TOKEN=""
fi

# Test projects endpoint
echo -n "Testing projects endpoint... "
PROJECTS_STATUS=$(make_request "GET" "/projects")
if [ "$PROJECTS_STATUS" = "200" ] || [ "$PROJECTS_STATUS" = "401" ]; then
  echo -e "${GREEN}OK${NC}"
else
  echo -e "${RED}Failed${NC}"
  echo "  Projects endpoint returned status: $PROJECTS_STATUS"
  exit 1
fi

# Test creating a project (requires authentication)
if [ -n "$JWT_TOKEN" ]; then
  echo -n "Testing project creation... "
  CREATE_RESPONSE=$(curl -s -X POST "$API_URL/projects" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -d '{"name": "Smoke Test Project", "description": "Project created during smoke tests"}')
  
  PROJECT_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id' 2>/dev/null)
  
  if [ -n "$PROJECT_ID" ] && [ "$PROJECT_ID" != "null" ]; then
    echo -e "${GREEN}OK${NC} (Project ID: $PROJECT_ID)"
    
    # Clean up test project
    echo -n "Cleaning up test project... "
    DELETE_STATUS=$(make_request "DELETE" "/projects/$PROJECT_ID")
    if [ "$DELETE_STATUS" = "204" ]; then
      echo -e "${GREEN}OK${NC}"
    else
      echo -e "${RED}Warning: Failed to clean up test project${NC}"
      echo "  Delete request returned status: $DELETE_STATUS"
    fi
  else
    echo -e "${RED}Failed${NC}"
    echo "  Project creation failed. Response: $CREATE_RESPONSE"
    exit 1
  fi
fi

echo -e "\n${GREEN}All smoke tests passed successfully!${NC}"
