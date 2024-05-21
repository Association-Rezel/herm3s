#!/bin/bash

#I don't want to have the output of this next command in my console 
# (docker network ls -q | xargs docker network rm) > /dev/null 2>&1

#run commande to up docker compose
docker-compose up -d --force-recreate --build

#wait the end of the container unit_tests
test=$(docker ps | grep unit_tests)
while [ -n "$test" ]; do
    test=$(docker ps | grep unit_tests)
    sleep 1
done

#show logs of the container unit_tests
docker logs unit_tests

# (docker network ls -q | xargs docker network rm) > /dev/null 2>&1