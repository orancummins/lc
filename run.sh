#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
PORT="${PORT:-2009}"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS_FILE="$SCRIPT_DIR/requirements.txt"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[run] Creating virtual environment at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [[ -f "$REQUIREMENTS_FILE" ]]; then
  echo "[run] Installing Python dependencies from requirements.txt"
  python -m pip install --disable-pip-version-check -r "$REQUIREMENTS_FILE"
fi

existing_pids="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "$existing_pids" ]]; then
  echo "[run] Stopping existing process(es) on port $PORT: $existing_pids"
  kill $existing_pids 2>/dev/null || true

  # Wait briefly for graceful shutdown, then force if still listening.
  for _ in {1..10}; do
    sleep 0.2
    if ! lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
      break
    fi
  done

  remaining_pids="$(lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true)"
  if [[ -n "$remaining_pids" ]]; then
    echo "[run] Force-stopping stubborn process(es): $remaining_pids"
    kill -9 $remaining_pids 2>/dev/null || true
  fi
fi

echo "[run] Starting app on http://localhost:$PORT"
exec python app.py
