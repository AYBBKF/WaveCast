#!/bin/sh
# Démarrage du conteneur : secrets générés sur le serveur, migrations, contenu de
# démonstration, admin initial éventuel, puis Gunicorn.
set -e
if [ -z "$ACADEMY_SECRET_KEY" ] && [ -r /secrets/secret_key ]; then
  ACADEMY_SECRET_KEY="$(cat /secrets/secret_key)"
  export ACADEMY_SECRET_KEY
fi
if [ -z "$DATABASE_URL" ] && [ -r /secrets/db_password ]; then
  DATABASE_URL="postgres://academy:$(cat /secrets/db_password)@${DB_HOST:-db}:5432/academy"
  export DATABASE_URL
fi
python manage.py migrate --noinput
python manage.py seed_demo
python manage.py bootstrap_admin
exec gunicorn academy_site.wsgi \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout 60 \
  --access-logfile - \
  --forwarded-allow-ips "*"
