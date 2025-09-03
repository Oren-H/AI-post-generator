#!/usr/bin/env bash
set -euo pipefail

# Change to project root (directory of this script)
cd "$(dirname "$0")"

# Activate local venv if present
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  source "venv/bin/activate"
fi

# Default port if not provided
export PORT=${PORT:-7860}

# Launch Gradio GUI
python -m src.gui


