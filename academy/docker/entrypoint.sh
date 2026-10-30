#!/bin/sh
# Démarrage du conteneur : migrations, contenu de démonstration, admin initial, puis Gunicorn.
set -e
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py bootstrap_admin
exec gunicorn academy_site.wsgi \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 60 \
  --access-logfile - \
  --forwarded-allow-ips "*"
