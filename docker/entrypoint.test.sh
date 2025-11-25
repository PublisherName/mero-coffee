#!/bin/sh
uv sync --frozen --no-install-project
uv run manage.py migrate
uv run python manage.py seed_payment_gateways
uv run manage.py collectstatic --no-input
uv run manage.py test -v 3
