#!/bin/bash

docker-compose build
docker-compose up
docker container prune -f
docker image prune -f