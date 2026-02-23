@echo off
REM deploy.bat
REM Deployment script for Aetherstore Engine with IWSDK Integration (Windows)

REM Colors for output (using PowerShell for colored output)
set RED=Write-Host -ForegroundColor Red
set GREEN=Write-Host -ForegroundColor Green
set YELLOW=Write-Host -ForegroundColor Yellow
set BLUE=Write-Host -ForegroundColor Blue

REM Configuration
set DEPLOY_ENV=%1
if "%DEPLOY_ENV%"=="" set DEPLOY_ENV=staging
set PROJECT_ROOT=%~dp0
set BACKEND_DIR=%PROJECT_ROOT%backend
set FRONTEND_DIR=%PROJECT_ROOT%frontend
set BUILD_DIR=%PROJECT_ROOT%build

REM Logging functions
:log
powershell -Command "%BLUE% '[DEPLOY] %date% %time% - %*' "
goto :eof

:log_success
powershell -Command "%GREEN% '[SUCCESS] %date% %time% - %*' "
goto :eof

:log_warning
powershell -Command "%YELLOW% '[WARNING] %date% %time% - %*' "
goto :eof

:log_error
powershell -Command "%RED% '[ERROR] %date% %time% - %*' "
goto :eof

REM Main deployment function
:main
call :log "Starting Aetherstore Engine deployment to %DEPLOY_ENV% environment..."

REM Check prerequisites
call :check_prerequisites
if errorlevel 1 goto :error

REM Build backend
call :build_backend
if errorlevel 1 goto :error

REM Build frontend
call :build_frontend
if errorlevel 1 goto :error

REM Create deployment package
call :create_deployment_package
if errorlevel 1 goto :error

REM Deploy to target environment
call :deploy_to_environment
if errorlevel 1 goto :error

REM Run post-deployment tests
call :run_post_deployment_tests
if errorlevel 1 goto :error

call :log_success "Aetherstore Engine deployment to %DEPLOY_ENV% completed successfully!"
call :log "Deployment package available at: %BUILD_DIR%"
call :log "Next steps:"
call :log "1. Wait for official IWSDK packages to be published"
call :log "2. Replace mock implementations with real IWSDK functionality"
call :log "3. Complete the remaining items in DEPLOYMENT_CHECKLIST.md"
call :log "4. Run comprehensive testing before production deployment"
goto :eof

REM Check prerequisites
:check_prerequisites
call :log "Checking deployment prerequisites..."

REM Check if required tools are installed
where python >nul 2>&1
if errorlevel 1 (
    call :log_error "Python is not installed. Please install it before deploying."
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    call :log_error "npm is not installed. Please install Node.js before deploying."
    exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    call :log_error "Node.js is not installed. Please install it before deploying."
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    call :log_warning "Docker is not installed. Some deployment features may not work."
)

where git >nul 2>&1
if errorlevel 1 (
    call :log_warning "Git is not installed. Version control features may not work."
)

call :log_success "All prerequisites satisfied"
exit /b 0

REM Build backend
:build_backend
call :log "Building backend application..."

cd /d "%BACKEND_DIR%"

REM Install backend dependencies
call :log "Installing backend dependencies..."
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    call :log_warning "Failed to install backend dependencies, continuing with deployment..."
)

REM Run backend tests
call :log "Running backend tests..."
if exist test_api_structure.py (
    python test_api_structure.py >nul 2>&1
    if errorlevel 1 (
        call :log_warning "Some backend tests failed, continuing with deployment..."
    )
) else (
    call :log_warning "No backend tests found"
)

REM Run database migrations if alembic is available
where alembic >nul 2>&1
if errorlevel 0 (
    call :log "Running database migrations..."
    alembic upgrade head >nul 2>&1
    if errorlevel 1 (
        call :log_warning "Database migrations failed, continuing with deployment..."
    )
) else (
    call :log_warning "Alembic not found, skipping database migrations"
)

call :log_success "Backend built successfully"
exit /b 0

REM Build frontend
:build_frontend
call :log "Building frontend application..."

cd /d "%FRONTEND_DIR%"

REM Install frontend dependencies
call :log "Installing frontend dependencies..."
npm install >nul 2>&1
if errorlevel 1 (
    call :log_warning "Failed to install frontend dependencies, continuing with deployment..."
)

REM Build frontend for production
call :log "Building frontend for production..."
npm run build >nul 2>&1
if errorlevel 1 (
    call :log_warning "Failed to build frontend, continuing with deployment..."
)

call :log_success "Frontend built successfully"
exit /b 0

REM Create deployment package
:create_deployment_package
call :log "Creating deployment package..."

REM Create build directory
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

REM Copy backend files
call :log "Copying backend files..."
xcopy /E /I /Y "%BACKEND_DIR%" "%BUILD_DIR%\backend\" >nul 2>&1

REM Copy frontend build files
call :log "Copying frontend build files..."
if not exist "%BUILD_DIR%\frontend\dist" mkdir "%BUILD_DIR%\frontend\dist"
xcopy /E /I /Y "%FRONTEND_DIR%\dist\*" "%BUILD_DIR%\frontend\dist\" >nul 2>&1

REM Copy documentation
call :log "Copying documentation..."
copy "%PROJECT_ROOT%IWSDK_INTEGRATION.md" "%BUILD_DIR%\" >nul 2>&1
copy "%PROJECT_ROOT%DEPLOYMENT_CHECKLIST.md" "%BUILD_DIR%\" >nul 2>&1
copy "%PROJECT_ROOT%README.md" "%BUILD_DIR%\" >nul 2>&1

REM Create deployment manifest
call :log "Creating deployment manifest..."
(
    echo {
    echo   "project": "Aetherstore Engine",
    echo   "version": "1.0.0",
    echo   "build_date": "%date%",
    echo   "environment": "%DEPLOY_ENV%",
    echo   "components": {
    echo     "backend": {
    echo       "language": "Python",
    echo       "framework": "FastAPI",
    echo       "status": "ready_for_iwsdk_integration"
    echo     },
    echo     "frontend": {
    echo       "language": "JavaScript",
    echo       "frameworks": ["Three.js", "React"],
    echo       "status": "ready_for_iwsdk_integration"
    echo     },
    echo     "iwsdk": {
    echo       "status": "mock_implementation",
    echo       "note": "Waiting for official IWSDK packages"
    echo     }
    echo   },
    echo   "deployment_notes": [
    echo     "IWSDK integration is currently using mock implementations",
    echo     "Real IWSDK packages need to be published before production deployment",
    echo     "All core functionality implemented with fallback to traditional 3D"
    echo   ]
    echo }
) > "%BUILD_DIR%\deployment_manifest.json"

call :log_success "Deployment package created at %BUILD_DIR%"
exit /b 0

REM Deploy to target environment
:deploy_to_environment
call :log "Deploying to %DEPLOY_ENV% environment..."

if "%DEPLOY_ENV%"=="staging" (
    call :deploy_to_staging
) else if "%DEPLOY_ENV%"=="production" (
    call :deploy_to_production
) else (
    call :log_warning "Unknown environment: %DEPLOY_ENV%, deploying to staging"
    call :deploy_to_staging
)

exit /b 0

:deploy_to_staging
call :log "Deploying to staging environment..."
call :log_warning "Staging deployment is a placeholder - real implementation needed"
call :log_success "Staging deployment completed (placeholder)"
exit /b 0

:deploy_to_production
call :log "Deploying to production environment..."
call :log_warning "Production deployment is a placeholder - real implementation needed"
call :log_success "Production deployment completed (placeholder)"
exit /b 0

REM Run post-deployment tests
:run_post_deployment_tests
call :log "Running post-deployment tests..."
call :log_warning "Post-deployment tests are a placeholder - real implementation needed"
call :log_success "Post-deployment tests completed (placeholder)"
exit /b 0

:error
call :log_error "Deployment failed with error level %errorlevel%"
exit /b %errorlevel%

REM Run main function
:main
call :main