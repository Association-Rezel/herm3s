#!/bin/bash

#I don't want to have the output of this next command in my console 
# (docker network ls -q | xargs docker network rm) > /dev/null 2>&1

docker compose -f docker-compose.unit_tests.yaml down -t 2

#run commande to up docker compose
docker compose -f docker-compose.unit_tests.yaml up -d --build

docker stop test_mongodb-import
docker rm test_mongodb-import

#wait the end of the container unit_tests
test=$(docker ps | grep unit_tests)
while [ -n "$test" ]; do
    test=$(docker ps | grep unit_tests)
    sleep 1
done

#show logs of the container test_api_hermes
docker logs test_api_hermes
#show logs of the container unit_tests
docker logs unit_tests

docker compose -f docker-compose.unit_tests.yaml down -t 2
