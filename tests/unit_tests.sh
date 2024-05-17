#!/bin/bash

BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'


echo -e "${BLUE}Beginning unit tests...${NC}"

# ----------------------------------------
# Unit tests 1: curl on '/'
# ----------------------------------------
echo -e "${YELLOW}Running unit test 1: curl on '/'${NC}"
http_code=$(curl -s -o /dev/null -w "%{http_code}" http://api_hermes:8000/)
if [ $http_code -eq 200 ]; then
    echo -e "${GREEN}Unit test 1 passed with code ${http_code} !${NC}"
else
    echo -e "${RED}Unit test 1 failed with code ${http_code} !${NC}"
fi

# ----------------------------------------
# Unit tests 2: get error 400 invalid mac
# ----------------------------------------

echo -e "${YELLOW}Running unit test 2: get error 400 invalid mac${NC}"

echo -e "curl on http://api_hermes/v1/config/ac2350/invalid_mac..."


http_code=$(curl -s -o /dev/null -w "%{http_code}" http://api_hermes:8000/v1/config/ac2350/invalid_mac)
message=$(curl -s http://api_hermes:8000/v1/config/ac2350/invalid_mac)

if [ $http_code -eq 400 ]; then
    echo -e "${GREEN}Unit test 2 passed with with code: ${http_code} and message: ${message} !${NC}"
else
    echo -e "${RED}Unit test 2 failed with code: ${http_code} and message: ${message} !${NC}"
fi

# ----------------------------------------
# Unit tests 3:
# ----------------------------------------








# ----------------------------------------
# Unit tests : ping ipv6 of hermes 
# ----------------------------------------

# echo -e "${YELLOW}Running unit test 3: ping ipv6 of hermes${NC}"

# echo -e "ping6 on api_hermes..."

# ping6 -c 4  api_hermes