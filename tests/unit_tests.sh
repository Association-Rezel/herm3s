#!/bin/bash
 
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'


echo -e "Beginning unit tests..."

# ----------------------------------------
# Unit tests 1
# ----------------------------------------
echo -e "${YELLOW}Running unit test 1: curl on '/'${NC}"
result=$(curl -s -o /dev/null -w "%{http_code}" http://api_hermes:8000/)
if [ $result -eq 200 ]; then
    echo -e "${GREEN}Unit test 1 passed with code ${result} !${NC}"
else
    echo -e "${RED}Unit test 1 failed with code ${result} !${NC}"
fi