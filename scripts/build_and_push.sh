#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Run the application
pushd $SCRIPT_DIR/.. || exit

docker compose --file ./docker/docker-compose.yaml build
docker compose --file ./docker/docker-compose.yaml push
