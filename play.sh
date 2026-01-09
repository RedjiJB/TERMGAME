#!/bin/bash
# TermGame Launcher - Simple script to activate venv and start game

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/.venv/bin/activate"

# Launch TermGame TUI
termgame tui
