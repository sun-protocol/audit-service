FROM node:20-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:/root/.local/bin:$PATH \
    OPENCODE_BIN=/usr/local/bin/opencode

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    git \
    bash \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt /app/backend/requirements.txt
COPY frontend/package.json /app/frontend/package.json
COPY frontend/package-lock.json /app/frontend/package-lock.json

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install -r /app/backend/requirements.txt
RUN npm install --prefix /app/frontend
RUN curl -fsSL https://opencode.ai/install | bash
RUN bash -lc 'OPENCODE_PATH="$(command -v opencode || true)"; test -n "$OPENCODE_PATH"; ln -sf "$OPENCODE_PATH" /usr/local/bin/opencode'

COPY . /app

RUN chmod +x /app/docker/docker-start.sh

EXPOSE 5173 8000

CMD ["/app/docker/docker-start.sh"]
