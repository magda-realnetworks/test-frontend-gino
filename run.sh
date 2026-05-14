#!/usr/bin/env bash
set -euo pipefail

SESSION_NAME="streamlit_chatbot"
APP_DIR="/home/gino/test_frontend_gino"
VENV_ACTIVATE="$APP_DIR/.venv/bin/activate"
APP_CMD="streamlit run app.py --server.address 0.0.0.0 --server.port 8501"

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is not installed. Please install tmux first." >&2
  exit 1
fi

if [ ! -f "$VENV_ACTIVATE" ]; then
  echo "Virtualenv not found at $VENV_ACTIVATE" >&2
  exit 1
fi

# If session exists, do nothing
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "Session '$SESSION_NAME' already running."
  exit 0
fi

# Start detached session
TMUX_CMD="cd $APP_DIR && . $VENV_ACTIVATE && $APP_CMD"

tmux new-session -d -s "$SESSION_NAME" "$TMUX_CMD"

echo "Started Streamlit app in tmux session '$SESSION_NAME'."
