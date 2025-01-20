#!/usr/bin/env bash

set -e

cd tastify

git pull
docker compose --file ./docker/docker-compose.yaml stop
docker compose --file ./docker/docker-compose.yaml up --build -d remote
