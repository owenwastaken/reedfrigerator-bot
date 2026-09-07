FROM ghcr.io/astral-sh/uv:python3.14-alpine

WORKDIR /app

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

RUN addgroup -g 1001 -S reedfrigerator && \
    adduser -S reedfrigerator  1001

# USER reedfrigerator
ENTRYPOINT ["python3", "-O", "-u", "-m", "reedfrigerator_bot"]
