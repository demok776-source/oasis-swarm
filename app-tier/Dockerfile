FROM python:3.11-alpine

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    gcc \
    python3-dev \
    musl-dev

COPY requirements.txt .
RUN pip install uv && uv pip install --system -r requirements.txt

COPY gunicorn_conf.py .
COPY src/ ./src/

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn_conf.py", "src.main:app"]
