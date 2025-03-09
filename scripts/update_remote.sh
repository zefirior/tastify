#!/usr/bin/env bash

set -e

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sed "s|BRANCH_NAME|$(git branch --show-current)|g" $SCRIPT_DIR/update_remote.sh.tpl | ssh tastify "bash -s"
