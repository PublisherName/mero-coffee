FROM python:3.13-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_HTTP_TIMEOUT=120 \
    UV_LINK_MODE=copy \
    DEBIAN_FRONTEND=noninteractive \
    CODE_PATH="/code" \
    VENV_PATH="/code/.venv"

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

# Development stage
FROM base AS development

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc postgresql-client nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $CODE_PATH
COPY . $CODE_PATH
ENTRYPOINT ["/code/docker/entrypoint.dev.sh"]

# Testing stage
FROM base AS testing

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc postgresql-client nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $CODE_PATH
COPY . $CODE_PATH
ENTRYPOINT ["/code/docker/entrypoint.test.sh"]

# Production build stage
FROM base AS production-build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR $CODE_PATH
COPY pyproject.toml uv.lock ./
RUN uv venv --seed && \
    uv sync --frozen --no-dev --extra production --no-install-project && \
    find $VENV_PATH -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find $VENV_PATH -type f -name "*.pyc" -delete && \
    find $VENV_PATH -type f -name "*.pyo" -delete

# Production stage
FROM python:3.13-slim AS production

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/code/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /code
COPY --from=production-build /code/.venv /code/.venv
COPY . /code
ENTRYPOINT ["/code/docker/entrypoint.prod.sh"]
