#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Run the application
pushd $SCRIPT_DIR/.. || exit
reflex run
popd || exit
