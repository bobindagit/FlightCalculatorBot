#!/bin/bash

docker build --tag flight_calculator_bot .
docker run -it --name flight_calculator_bot --env-file "env" flight_calculator_bot
docker container prune -f
docker image prune -f