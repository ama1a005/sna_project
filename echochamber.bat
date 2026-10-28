@echo off
set SCRIPT_DIR=%~dp0
if exist "%SCRIPT_DIR%.venv\Scripts\echochamber.exe" (
    "%SCRIPT_DIR%.venv\Scripts\echochamber.exe" %*
) else (
    python -m echochamber %*
)
