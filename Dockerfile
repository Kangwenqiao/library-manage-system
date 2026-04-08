FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.7.6 /uv /uvx /bin/

COPY pyproject.toml uv.lock .python-version README.md /app/
RUN uv sync --frozen --no-dev

COPY . /app

RUN mkdir -p /app/logging /app/staticfiles \
    && uv run python manage.py migrate \
    && uv run python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "--config", "gunicorn-cfg.py", "core.wsgi"]
