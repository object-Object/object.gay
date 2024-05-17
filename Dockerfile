FROM ghcr.io/astral-sh/uv AS uv

FROM python:3.11

COPY --from=uv /uv /usr/bin/uv

WORKDIR /app

COPY pyproject.toml ./
COPY src/object_gay/__init__.py src/object_gay/

RUN --mount=type=cache,target=/root/.cache/uv \
uv pip install --system -e '.[runtime]'

COPY src/object_gay/ src/object_gay/

CMD python -m $MODULE

HEALTHCHECK \
    --interval=1m \
    --timeout=30s \
    --start-period=2m \
    --start-interval=15s \
    --retries=3 \
    CMD ["python", "-m", "object_gay.health_check"]
