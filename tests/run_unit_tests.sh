#!/bin/bash

#run commande to up docker compose
docker-compose up -d --build

#wait the end of the container unit_tests
test=$(docker ps | grep unit_tests)
while [ -n "$test" ]; do
    test=$(docker ps | grep unit_tests)
    sleep 1
done

#show logs of the container unit_tests
docker logs unit_tests

