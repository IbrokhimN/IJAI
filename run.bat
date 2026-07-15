@echo off
setlocal
set DIR=%~dp0
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo Python not found. Install it from https://python.org
  exit /b 1
)
python "%DIR%launch.py" %*
