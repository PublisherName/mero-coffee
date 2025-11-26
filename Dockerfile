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
    postgresql-client && \
    curl -fsSL https://deb.nodesource.com/setup_25.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# UV base
FROM base AS uv-base

COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /bin/

# Development stage
FROM uv-base AS development

WORKDIR $CODE_PATH

COPY . $CODE_PATH

ENTRYPOINT ["/code/docker/entrypoint.dev.sh"]

# Testing stage
FROM uv-base AS testing

WORKDIR $CODE_PATH

# Copy source code
COPY . $CODE_PATH

# Use testing entrypoint
ENTRYPOINT ["/code/docker/entrypoint.test.sh"]


# Production build stage
FROM uv-base AS production-build

WORKDIR $CODE_PATH

COPY pyproject.toml uv.lock ./

# Install all dependencies required for production
RUN uv venv --seed
RUN uv sync --frozen --no-dev --extra production --no-install-project

# Production stage
FROM base AS production

WORKDIR $CODE_PATH

COPY --from=production-build $VENV_PATH $VENV_PATH
COPY . $CODE_PATH

ENV PATH="$VENV_PATH/bin:$PATH"

ENTRYPOINT ["/code/docker/entrypoint.prod.sh"]
