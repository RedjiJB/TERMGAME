@echo off
REM TermGame Launcher - Simple batch script to start the game

REM Activate virtual environment and run TermGame
call "%~dp0.venv\Scripts\activate.bat"
termgame tui
