#!/usr/bin/env bash

set -e

cd tastify

git fetch
git reset --hard origin/main

docker compose --file ./docker/remote.docker-compose.yaml stop
docker compose --file ./docker/remote.docker-compose.yaml up --build -d
