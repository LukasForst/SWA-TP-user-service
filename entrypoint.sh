#!/bin/bash
set -euo pipefail

# wait on db
# we use automatic migration as this is dev environment
./wait-for-it.sh "${POSTGRES_URL}" -- flask db upgrade

# startup servicce
gunicorn --bind 0.0.0.0:8080 --log-level WARNING app:app