#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Starting docker compose stack..."
docker compose up -d --build

echo "Done."
echo "  App:     http://localhost:8501"
echo "  Grafana: http://localhost:3000"
echo "  pgAdmin: http://localhost:5050"