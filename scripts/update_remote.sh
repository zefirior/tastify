#!/usr/bin/env bash

set -e

cd tastify

git fetch
git reset --hard origin/liinda/persist-db-volumes-on-remote

docker compose --file ./docker/remote.docker-compose.yaml stop
docker compose --file ./docker/remote.docker-compose.yaml up --build -d
