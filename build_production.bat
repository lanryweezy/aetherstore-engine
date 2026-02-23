@echo off
REM Aetherstore Engine - Production Build Script
REM Use this script to build the application for production deployment

echo.
echo ================================================
echo Aetherstore Engine - Production Build Process
echo ================================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js before proceeding.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed. Please install Python before proceeding.
    echo Download from: https://www.python.org/
    pause
    exit /b 1
)

echo 1. Building Frontend Application...
echo.

REM Navigate to frontend directory and build
cd frontend

REM Install frontend dependencies
echo Installing frontend dependencies...
npm install --no-audit --no-fund
if %errorlevel% neq 0 (
    echo ERROR: Failed to install frontend dependencies
    pause
    exit /b 1
)

REM Build frontend for production
echo Building frontend for production...
npm run build -- --mode=production
if %errorlevel% neq 0 (
    echo ERROR: Frontend build failed
    pause
    exit /b 1
)

echo Frontend build completed successfully!
echo.

REM Navigate to backend directory
cd ../backend

echo 2. Installing Backend Dependencies...
echo.

REM Install backend dependencies
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo Backend dependencies installed successfully!
echo.

REM Create production config
echo 3. Creating Production Configuration...
echo.

REM Create production config file if it doesn't exist
if not exist "production_config.py" (
    echo import os > production_config.py
    echo. >> production_config.py
    echo # Production Configuration >> production_config.py
    echo SECRET_KEY = os.environ.get('AETHERSTORE_SECRET_KEY', 'change_me_in_production') >> production_config.py
    echo. >> production_config.py
    echo DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///production.db') >> production_config.py
    echo. >> production_config.py
    echo # Security Settings >> production_config.py
    echo DEBUG = False >> production_config.py
    echo ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com'] >> production_config.py
    echo SECURE_SSL_REDIRECT = True >> production_config.py
    echo SESSION_COOKIE_SECURE = True >> production_config.py
    echo CSRF_COOKIE_SECURE = True >> production_config.py
    echo SECURE_BROWSER_XSS_FILTER = True >> production_config.py
    echo SECURE_CONTENT_TYPE_NOSNIFF = True >> production_config.py
    echo X_FRAME_OPTIONS = 'DENY' >> production_config.py
    echo. >> production_config.py
    echo print("Production configuration created. Please review and customize it for your environment.") >> production_config.py
)

echo Production configuration created.
echo.

REM Run backend tests if available
echo 4. Running Backend Tests...
echo.

REM Check if tests exist and run them
if exist "test_suite.py" (
    python test_suite.py
    if %errorlevel% neq 0 (
        echo WARNING: Some tests failed. Please review before deployment.
    ) else (
        echo All backend tests passed!
    )
) else (
    echo No backend test suite found. Skipping backend tests.
)

echo.

REM Final checks
echo 5. Final Build Checks...
echo.

REM Check if frontend dist was created
if not exist "../frontend/dist" (
    echo ERROR: Frontend build failed - dist directory not found
    pause
    exit /b 1
)

echo Build directories:
echo   Frontend: ../frontend/dist
echo   Backend: ./ (ready to deploy)
echo.

REM Create deployment package
echo 6. Creating Deployment Package...
echo.

REM Create a deployment package with both frontend and backend
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set PACKAGE_NAME=aetherstore_engine_%TIMESTAMP%
mkdir ..\%PACKAGE_NAME%

REM Copy frontend build
xcopy /E /I /Y frontend\dist ..\%PACKAGE_NAME%\frontend\dist\ >nul

REM Copy backend files (excluding development files)
xcopy /E /I /Y backend\*.py ..\%PACKAGE_NAME%\backend\ >nul
xcopy /E /I /Y backend\requirements.txt ..\%PACKAGE_NAME%\backend\ >nul
xcopy /E /I /Y backend\schema.sql ..\%PACKAGE_NAME%\backend\ >nul

REM Copy configuration files
if exist production_config.py (
    copy production_config.py ..\%PACKAGE_NAME%\backend\ >nul
)

REM Copy deployment documentation
copy ..\PRODUCTION_DEPLOYMENT.md ..\%PACKAGE_NAME%\ >nul
copy ..\README.md ..\%PACKAGE_NAME%\ >nul

echo Deployment package created: ..\%PACKAGE_NAME%
echo.

REM Provide deployment instructions
echo ================================================
echo BUILD COMPLETED SUCCESSFULLY!
echo ================================================
echo.
echo Deployment Package: ..\%PACKAGE_NAME%
echo.
echo Next Steps:
echo 1. Upload the package to your server
echo 2. Set up environment variables (see PRODUCTION_DEPLOYMENT.md)
echo 3. Configure your web server (Nginx/Apache)
echo 4. Set up SSL certificates
echo 5. Run database migrations
echo 6. Start the application services
echo.
echo For detailed deployment instructions, see PRODUCTION_DEPLOYMENT.md
echo.
echo Frontend assets are in the /frontend/dist directory
echo Backend code is in the /backend directory
echo.
echo Please review all configuration files before deployment!
echo.
pause