FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r requirements.txt

COPY pyproject.toml alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY scripts/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/sh", "./entrypoint.sh"]
