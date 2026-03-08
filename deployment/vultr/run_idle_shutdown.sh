#!/bin/bash
# Run idle_shutdown.py with .env loaded. Use from cron:
#   */15 * * * * /path/to/speedray/deployment/vultr/run_idle_shutdown.sh
# Project root is auto-detected (parent of deployment/).
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"
set -a
[ -f .env ] && . ./.env
set +a
. ./venv/bin/activate
exec python deployment/vultr/idle_shutdown.py
