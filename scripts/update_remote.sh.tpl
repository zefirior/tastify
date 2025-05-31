#!/usr/bin/env bash

set -e

cd tastify

git fetch
git reset --hard origin/BRANCH_NAME

docker compose --file ./docker/remote.docker-compose.yaml stop
docker container prune -f
docker volume prune -f
docker compose --file ./docker/remote.docker-compose.yaml up --build -d || {
  docker compose --file ./docker/remote.docker-compose.yaml logs --tail=200
  exit 1
}
