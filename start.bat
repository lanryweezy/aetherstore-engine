@echo off
REM Aetherstore Engine Startup Script
REM Starts both backend and frontend servers

echo Starting Aetherstore Engine...

REM Start backend server in a new command window
start "Aetherstore Backend" cmd /k "cd /d C:\Users\lanry\Desktop\3D fashion store\backend && python -m main"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server in a new command window
start "Aetherstore Frontend" cmd /k "cd /d C:\Users\lanry\Desktop\3D fashion store\frontend && npx http-server"

echo Aetherstore Engine is starting...
echo Backend server will run on http://localhost:8000
echo Frontend will be available at http://localhost:8080
echo Admin interface available at http://localhost:8080/admin

pause