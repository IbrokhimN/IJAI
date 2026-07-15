#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="python3"
command -v python3 >/dev/null 2>&1 || PYTHON_BIN="python"
exec "$PYTHON_BIN" "$DIR/launch.py" "$@"
