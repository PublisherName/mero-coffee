#!/bin/sh

if [ "$CELERY_WORKER" = "true" ]
then
    exec gosu 1000:1000 uv run celery -A root worker -l info
else
    ./manage.py collectstatic --no-input
    ./manage.py migrate --no-input
    ./manage.py loaddata fixtures/nepal_cities_light.json
    ./manage.py seed_payment_gateways
    ./manage.py seed_email_templates
    ./manage.py setup_roles
    gunicorn root.asgi:application -k uvicorn.workers.UvicornH11Worker -b 0.0.0.0:8000
fi
