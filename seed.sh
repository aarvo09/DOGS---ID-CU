#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH="$DIR/packages:$DIR:$PYTHONPATH"

python3 -m app.seed
