FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      ffmpeg fonts-dejavu-core fonts-noto-core fonts-noto-ui-core fonts-noto-color-emoji \
      libass9 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY chronoshorts ./chronoshorts
RUN pip install --no-cache-dir ".[edge]"

ENV CHRONO_WORKDIR=/data/productions \
    CHRONO_ASSETS_DIR=/data/assets \
    PYTHONUNBUFFERED=1

VOLUME ["/data"]
ENTRYPOINT ["chronoshorts"]
CMD ["bot"]
