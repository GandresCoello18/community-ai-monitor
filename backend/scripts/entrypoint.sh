#!/bin/sh
set -e

alembic upgrade head

if [ "${SEED_DEMO_DATA:-true}" = "true" ] && [ "${APP_ENV:-development}" = "development" ]; then
  python -m app.cli.seed
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
