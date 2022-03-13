#!/bin/bash

docker build --file "Dockerfile_tests" --tag flight_calculator_tests .
docker run -it --name flight_calculator_tests --env-file "env" flight_calculator_tests
docker container prune -f
docker image prune -f