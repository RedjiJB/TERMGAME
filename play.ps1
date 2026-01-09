#!/usr/bin/env pwsh
# TermGame Launcher - Simple script to activate venv and start game

# Activate virtual environment
& "$PSScriptRoot\.venv\Scripts\Activate.ps1"

# Launch TermGame TUI
termgame tui
