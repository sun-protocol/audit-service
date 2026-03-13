#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="${IMAGE_NAME:-audit-service}"
CONTAINER_NAME="${CONTAINER_NAME:-audit-service-local}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
GIT_SSL_NO_VERIFY="${GIT_SSL_NO_VERIFY:-false}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCKER_DIR="$ROOT_DIR/docker"

if docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"; then
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
fi

docker build -f "$DOCKER_DIR/Dockerfile" -t "$IMAGE_NAME" "$ROOT_DIR"

docker run --rm \
  --name "$CONTAINER_NAME" \
  -e GIT_SSL_NO_VERIFY="${GIT_SSL_NO_VERIFY}" \
  -p ${FRONTEND_PORT}:5173 \
  -p ${BACKEND_PORT}:8000 \
  "$IMAGE_NAME"
