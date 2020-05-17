#!/bin/bash
set -euo pipefail

# we use automatic migration as this is dev environment
flask db upgrade
# startup servicce
gunicorn --bind 0.0.0.0:8080 --log-level WARNING app:app