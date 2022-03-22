#!/bin/bash

docker container prune -f
docker image prune -f
docker image remove flightcalculator_python_app
docker-compose build
docker-compose up