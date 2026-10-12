@echo off
cd /d "%~dp0"
if not exist .env (
  echo Copy .env.example to .env and configure PostgreSQL first.
  exit /b 1
)
if not exist .venv python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
.venv\Scripts\python manage.py migrate
if errorlevel 1 exit /b 1
.venv\Scripts\python manage.py runserver 127.0.0.1:8000
