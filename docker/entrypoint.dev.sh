#!/bin/sh
uv sync --frozen --extra development --no-install-project
uv run manage.py tailwind install
uv run manage.py collectstatic --no-input
uv run manage.py migrate --no-input
uv run manage.py seed_payment_gateways
uv run manage.py tailwind dev
