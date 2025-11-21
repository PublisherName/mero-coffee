#!/usr/bin/env bash
set -o errexit

uv sync --frozen

python manage.py collectstatic --no-input

python manage.py migrate

python manage.py seed_payment_gateways
