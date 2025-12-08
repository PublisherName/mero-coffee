#!/bin/sh
uv sync --frozen --extra development --no-install-project
uv run manage.py tailwind install
uv run manage.py migrate
uv run manage.py loaddata fixtures/nepal_cities_light.json
uv run manage.py seed_payment_gateways
uv run manage.py collectstatic --no-input
uv run manage.py test -v 3
