
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    make \
    g++ \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    UV_PROJECT_ENVIRONMENT="/usr/local"



COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY . .

RUN uv sync --frozen --no-dev

CMD ["sh", "-c", "sleep 5 && uv run alembic upgrade head && uv run python -m uvicorn src.main:app --host 0.0.0.0 --port 8000"]