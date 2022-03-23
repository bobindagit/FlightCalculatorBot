#!/bin/bash

docker container prune -f
docker image prune -f
docker-compose build --no-cache
docker-compose up