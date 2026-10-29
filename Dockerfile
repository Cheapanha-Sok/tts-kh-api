# Builder stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

COPY . ./

# The model is copied separately into the final stage; drop it here so it isn't shipped twice
RUN find . -name '*.onnx' -not -path './.venv/*' -delete

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Final stage
FROM python:3.12-slim-bookworm AS final

WORKDIR /app

ARG APP_UID=10001
ARG APP_GID=10001
ARG MODEL_FILE=tts.onnx

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        espeak \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g ${APP_GID} appgroup && \
    useradd -u ${APP_UID} -g ${APP_GID} -s /usr/sbin/nologin -M appuser && \
    mkdir -p /var/log/tts-kh-gateway /app/src/tts_model && \
    touch /var/log/tts-kh-gateway/app.log /var/log/tts-kh-gateway/access.log && \
    chmod 666 /var/log/tts-kh-gateway/*.log

ENV VIRTUAL_ENV="/app/.venv" \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=development

COPY --from=builder --chown=${APP_UID}:${APP_GID} /app /app

COPY ${MODEL_FILE} /app/src/tts_model/tts.onnx

USER appuser

EXPOSE 8081

CMD ["gunicorn", "app:app", "--worker-class", "uvicorn.workers.UvicornWorker", "--workers", "2", "--bind", "0.0.0.0:8081"]
