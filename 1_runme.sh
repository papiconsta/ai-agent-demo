#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Waiting for postgres, applying schema, and ingesting vector DB (db_queries/1_check_db.py)..."
docker compose exec -T app python db_queries/1_check_db.py