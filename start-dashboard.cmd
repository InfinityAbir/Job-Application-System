@echo off
rem Double-click to start the dashboard. Keep this window open while you use it; close it to stop.
cd /d "%~dp0"
echo Starting Job Pipeline dashboard at http://127.0.0.1:8765 ...
python ui\server.py
pause
