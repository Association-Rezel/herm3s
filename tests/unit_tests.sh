#!/bin/bash

BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
NC='\033[0m'


echo -e "${BLUE}Beginning unit tests...${NC}"

# ----------------------------------------
# Unit tests 1: curl on '/'
# ----------------------------------------
echo -e "${YELLOW}Running unit ${YELLOW}test 1${YELLOW}: curl on '/'${NC}"
http_code=$(curl -s -o /dev/null -w "%{http_code}" ${URL}/)
if [ $http_code -eq 200 ]; then
    echo -e "${GREEN}Unit test 1 passed with code ${http_code} !${NC}"
else
    echo -e "${RED}Unit test 1 failed with code ${http_code} !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 2: get error 400 invalid mac
# ----------------------------------------

echo -e "${YELLOW}Running unit ${YELLOW}test 2${YELLOW}: get error 400 invalid mac${NC}"

echo -e "curl on ${URL}${ENDPOINT_CONFIG}invalid_mac..."


http_code=$(curl -s -o /dev/null -w "%{http_code}" ${URL}${ENDPOINT_CONFIG}invalid_mac)
message=$(curl -s ${URL}${ENDPOINT_CONFIG}invalid_mac)

if [ $http_code -eq 400 ]; then
    echo -e "${GREEN}Unit test 2 passed with with code: ${http_code} and message: ${message} !${NC}"
else
    echo -e "${RED}Unit test 2 failed with code: ${http_code} and message: ${message} !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 3: test endpoint of default config
# ----------------------------------------

echo -e "${YELLOW}Running unit ${YELLOW}test 3${YELLOW}: test endpoint of default config${NC}"

echo -e "curl on ${URL}${ENDPOINT_DEFAULT_CONFIG}..."

http_code=$(curl -s -o /dev/null -w "%{http_code}" ${URL}${ENDPOINT_DEFAULT_CONFIG})
if [ $http_code -eq 200 ]; then
    echo -e "${GREEN}Unit test 3 passed with code ${http_code} !${NC}"
else
    echo -e "${RED}Unit test 3 failed with code ${http_code} !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 4: test receive default config file
# ----------------------------------------

echo -e "${YELLOW}Running unit test 4: test if ${NAME_DEFAULT_CONFIG_FILE_TEST} is received${NC}"

echo -e "wget on ${URL}${ENDPOINT_DEFAULT_CONFIG}..."

wget -q -O - ${URL}${ENDPOINT_DEFAULT_CONFIG} > ${PATH_DEFAULT_CONFIG_FILE_TEST}${NAME_DEFAULT_CONFIG_FILE_TEST}

if [ -f ${PATH_DEFAULT_CONFIG_FILE_TEST}${NAME_DEFAULT_CONFIG_FILE_TEST} ]; then
    echo -e "${GREEN}Unit test 4 passed: ${NAME_DEFAULT_CONFIG_FILE_TEST} received !${NC}"
else
    echo -e "${RED}Unit test 4 failed: no file received !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 5: test content of default config file
# ----------------------------------------

echo -e "${YELLOW}Running unit test 5: test content of ${NAME_DEFAULT_CONFIG_FILE_TEST} ${NC}"

echo -e "diff between ${NAME_DEFAULT_CONFIG_FILE} and ${NAME_DEFAULT_CONFIG_FILE_TEST}..."

if diff ${PATH_DEFAULT_CONFIG_FILE}${NAME_DEFAULT_CONFIG_FILE} ${PATH_DEFAULT_CONFIG_FILE_TEST}${NAME_DEFAULT_CONFIG_FILE_TEST} > /result ; then
    echo -e "${GREEN}Unit test 5 passed: ${NAME_DEFAULT_CONFIG_FILE_TEST} is the same as ${NAME_DEFAULT_CONFIG_FILE} !${NC}"
else
    echo -e "${RED}Unit test 5 failed: ${NAME_DEFAULT_CONFIG_FILE_TEST} is different from ${NAME_DEFAULT_CONFIG_FILE} !${NC}"
    echo -e "$(cat /result)${NC}"
    exit 1
fi


# ----------------------------------------
# Unit tests 6: test endpoint of config file
# ----------------------------------------

echo -e "${YELLOW}Running unit ${YELLOW}test 6${YELLOW}: test endpoint of config file${NC}"

echo -e "curl on ${URL}${ENDPOINT_CONFIG}${MAC}..."

http_code=$(curl -s -o /dev/null -w "%{http_code}" ${URL}${ENDPOINT_CONFIG}${MAC})
if [ $http_code -eq 200 ]; then
    echo -e "${GREEN}Unit test 6 passed with code ${http_code} !${NC}"
else
    echo -e "${RED}Unit test 6 failed with code ${http_code} !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 7: test receive default config file
# ----------------------------------------

echo -e "${YELLOW}Running unit test 7: test if ${NAME_CONFIG_FILE_TEST} is received${NC}"

echo -e "wget on ${URL}${ENDPOINT_CONFIG}${MAC}..."

wget -q -O - ${URL}${ENDPOINT_CONFIG}${MAC} > ${PATH_CONFIG_FILE_TEST}${NAME_CONFIG_FILE_TEST}

if [ -f ${PATH_CONFIG_FILE_TEST}${NAME_CONFIG_FILE_TEST} ]; then
    echo -e "${GREEN}Unit test 7 passed: ${NAME_CONFIG_FILE_TEST} received !${NC}"
else
    echo -e "${RED}Unit test 7 failed: no file received !${NC}"
    exit 1
fi

# ----------------------------------------
# Unit tests 8: test content of default config file
# ----------------------------------------

echo -e "${YELLOW}Running unit test 8: test content of ${NAME_CONFIG_FILE_TEST} ${NC}"

echo -e "diff between ${NAME_CONFIG_FILE} and ${NAME_CONFIG_FILE_TEST}..."

if diff ${PATH_CONFIG_FILE}${NAME_CONFIG_FILE} ${PATH_CONFIG_FILE_TEST}${NAME_CONFIG_FILE_TEST} > /result ; then
    echo -e "${GREEN}Unit test 8 passed: ${NAME_CONFIG_FILE_TEST} is the same as ${NAME_CONFIG_FILE} !${NC}"
else
    echo -e "${RED}Unit test 8 failed: ${NAME_CONFIG_FILE_TEST} is different from ${NAME_CONFIG_FILE} !${NC}"
    echo -e "$(cat /result)${NC}"
    exit 1
fi


# ----------------------------------------
# Unit tests : ping ipv6 of hermes 
# ----------------------------------------

# echo -e "${YELLOW}Running unit test 3: ping ipv6 of hermes${NC}"

# echo -e "ping6 on api_hermes..."

# ping6 -c 4  api_hermes