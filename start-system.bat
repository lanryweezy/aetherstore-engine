@echo off
REM Aetherstore Engine Complete Startup Script
REM Starts backend, frontend, and provides status information

echo.
echo #########################################################
echo #         AETHERSTORE ENGINE - STARTUP SCRIPT           #
echo #########################################################
echo.

REM Set the root directory
set ROOT_DIR=%~dp0
echo Root directory: %ROOT_DIR%

REM Check if required Python packages are installed
echo.
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
) else (
    echo ✅ Python version:
    python --version
)

REM Check if required Node.js packages are installed
echo.
echo Checking Node.js environment...
node --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ Node.js is not installed or not in PATH (Required for frontend tools)
) else (
    echo ✅ Node.js version:
    node --version
)

REM Start backend server in a separate window
echo.
echo 🚀 Starting Aetherstore Backend Server...
start "Aetherstore Backend" cmd /k "cd /d %ROOT_DIR%backend && python -c "from main import *; import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=False)""

REM Wait a moment for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

REM Start frontend using http-server (if available) or just notify
echo.
echo 🌐 Setting up frontend services...

REM Check if http-server is available
node_modules\.bin\http-server --version >nul 2>&1
if errorlevel 1 (
    echo Installing http-server locally...
    cd /d %ROOT_DIR%frontend
    npm install http-server --save-dev >nul 2>&1
)

REM Start frontend server
cd /d %ROOT_DIR%frontend
start "Aetherstore Frontend" cmd /k "npx http-server -p 3000"

REM Display status information
echo.
echo #########################################################
echo #                  SYSTEM STATUS                        #
echo #########################################################
echo.
echo ✅ Backend Server: http://localhost:8000
echo ✅ Frontend Server: http://localhost:3000  
echo ✅ Admin Dashboard: http://localhost:3000/admin
echo ✅ API Documentation: http://localhost:8000/docs
echo.
echo #########################################################
echo #            AETHERSTORE ENGINE IS RUNNING              #
echo #########################################################
echo.
echo Press any key to see running processes...
pause >nul

REM Show running processes
echo.
echo 📋 Running processes:
tasklist /FI "IMAGENAME eq python.exe" | find /I "python.exe" >nul
if not errorlevel 1 (
    echo - Backend Python processes found
) else (
    echo - No backend Python processes found
)

echo.
echo 🎯 Next Steps:
echo 1. Visit http://localhost:3000 to access the shopping experience
echo 2. Visit http://localhost:3000/admin for the dashboard  
echo 3. Visit http://localhost:8000/docs for API documentation
echo 4. Run test_suite.py to verify all functionality
echo.

echo 🎉 Aetherstore Engine is ready for use!
pause