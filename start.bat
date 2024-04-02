@echo off
python app.py
waitress-serve --port=8000 app:app
REM Start Nginx
start "" "C:nginx-1.24.0\nginx.exe"