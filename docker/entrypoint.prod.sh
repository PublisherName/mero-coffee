#!/bin/sh
./manage.py collectstatic --no-input
./manage.py migrate --no-input
./manage.py seed_payment_gateways
gunicorn root.asgi:application -k uvicorn.workers.UvicornH11Worker -b 0.0.0.0:8000
