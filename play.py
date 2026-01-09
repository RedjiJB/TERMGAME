#!/usr/bin/env python3
"""TermGame Launcher - Universal cross-platform launcher script."""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch TermGame with automatic virtual environment activation."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()

    # Determine virtual environment activation script based on OS
    if sys.platform == "win32":
        venv_activate = script_dir / ".venv" / "Scripts" / "activate.bat"
        python_exe = script_dir / ".venv" / "Scripts" / "python.exe"
    else:
        venv_activate = script_dir / ".venv" / "bin" / "activate"
        python_exe = script_dir / ".venv" / "bin" / "python"

    # Check if virtual environment exists
    if not python_exe.exists():
        print("Error: Virtual environment not found!")
        print(f"Expected: {python_exe}")
        print("\nPlease run setup first:")
        print("  pip install uv")
        print('  uv pip install -e ".[dev]"')
        sys.exit(1)

    # Launch termgame tui using the venv's Python
    try:
        subprocess.run([str(python_exe), "-m", "termgame.cli", "tui"], check=True)
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\nError launching TermGame: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
