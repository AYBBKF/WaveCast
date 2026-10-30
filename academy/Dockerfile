# Image de production de Flux Intelligent Academy (construction locale : docker build -t academy .)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACADEMY_MEDIA_ROOT=/data/media \
    ACADEMY_PRIVATE_ROOT=/data/private

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN useradd --uid 1000 --create-home app \
 && mkdir -p /data/media /data/private \
 && chown -R app:app /data /app \
 && ACADEMY_SECRET_KEY=collectstatic-only python manage.py collectstatic --noinput

USER app
EXPOSE 8000
CMD ["sh", "/app/docker/entrypoint.sh"]
