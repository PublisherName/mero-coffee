#!/bin/sh
uv sync --frozen --extra development --no-install-project
uv run manage.py collectstatic --no-input
uv run manage.py migrate --no-input
uv run python manage.py seed_payment_gateways
uv run manage.py runserver_plus 0.0.0.0:8000 || uv run manage.py runserver 0.0.0.0:8000
