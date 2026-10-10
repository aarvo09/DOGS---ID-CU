#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PYTHONPATH="$DIR/packages:$DIR:$PYTHONPATH"

echo "=========================================================="
echo "🐾 Starting Chandigarh University Dog Digital Identity API"
echo "📍 Listening at http://0.0.0.0:8000"
echo "📖 Swagger API Docs: http://localhost:8000/docs"
echo "=========================================================="

python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
