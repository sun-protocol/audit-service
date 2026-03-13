#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/app"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]]; then
    kill "$BACKEND_PID" >/dev/null 2>&1 || true
  fi
  if [[ -n "${FRONTEND_PID:-}" ]]; then
    kill "$FRONTEND_PID" >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

if [[ -f "$HOME/.bashrc" ]]; then
  source "$HOME/.bashrc"
fi

export PATH="/opt/venv/bin:$HOME/.local/bin:$PATH"
if [[ -x "/usr/local/bin/opencode" ]]; then
  export OPENCODE_BIN="/usr/local/bin/opencode"
elif command -v opencode >/dev/null 2>&1; then
  export OPENCODE_BIN="$(command -v opencode)"
fi

mkdir -p "$BACKEND_DIR/workspaces"

(
  cd "$BACKEND_DIR"
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
) &
BACKEND_PID=$!

(
  cd "$FRONTEND_DIR"
  exec npm run dev -- --host 0.0.0.0 --port 5173
) &
FRONTEND_PID=$!

echo "Audit Service is starting in Docker..."
echo "Frontend: http://0.0.0.0:5173"
echo "Backend:  http://0.0.0.0:8000"
echo "OpenCode: ${OPENCODE_BIN:-not-found}"

wait
