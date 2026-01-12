FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_HTTP_TIMEOUT=120 \
    UV_LINK_MODE=copy \
    DEBIAN_FRONTEND=noninteractive \
    CODE_PATH="/code" \
    VENV_PATH="/code/.venv"

RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    gosu \
    postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/


# Base for development, testing and tailwind build
FROM base AS node-base

RUN curl -fsSL https://deb.nodesource.com/setup_25.x | bash - && \
    apt-get install -y nodejs &&  \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Base for builder
FROM node-base AS builder

WORKDIR $CODE_PATH

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --extra development --no-install-project

COPY . $CODE_PATH

COPY .env.test.example $CODE_PATH/.env

RUN uv run manage.py tailwind install

RUN uv run manage.py tailwind build


# Development stage
FROM node-base AS development

WORKDIR $CODE_PATH

COPY . $CODE_PATH

COPY --from=builder $CODE_PATH/theme/static_src/node_modules $CODE_PATH/theme/static_src/node_modules

ENTRYPOINT ["/code/docker/entrypoint.dev.sh"]


# Testing stage
FROM node-base AS testing

WORKDIR $CODE_PATH

COPY . $CODE_PATH

COPY --from=builder $CODE_PATH/theme/static_src/node_modules $CODE_PATH/theme/static_src/node_modules

ENTRYPOINT ["/code/docker/entrypoint.test.sh"]


# Production build uv stage: Installs ONLY production deps
FROM base AS production-build-uv

WORKDIR $CODE_PATH

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --extra production --no-install-project


# Production stage
FROM base AS production

WORKDIR $CODE_PATH

COPY --from=production-build-uv $VENV_PATH $VENV_PATH

COPY . $CODE_PATH

COPY --from=builder $CODE_PATH/theme/static/css/dist/styles.css $CODE_PATH/theme/static/css/dist/styles.css

RUN groupadd -r -g 1000 celery && \
    useradd -r -u 1000 -g celery -d /home/celery -s /bin/sh celery && \
    mkdir -p /home/celery && \
    chown -R celery:celery $CODE_PATH /home/celery

ENV PATH="$VENV_PATH/bin:$PATH"

ENTRYPOINT ["/code/docker/entrypoint.prod.sh"]
