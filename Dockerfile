FROM python:3.14-slim

# uv binary, copied in from its official image (recommended by astral-sh)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install dependencies first so this layer is cached while only app code changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

# Now copy the rest of the app and install it
COPY . .
RUN uv sync --frozen

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "pages/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
