#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH="$DIR/packages:$DIR:$PYTHONPATH"

echo "Running complete Chandigarh University Dog Identity System test suite..."
python3 -m unittest discover -s tests -p "test_*.py" -v
