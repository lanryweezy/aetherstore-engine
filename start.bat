@echo off
SETLOCAL EnableDelayedExpansion

echo 🚀 Starting AetherStore Engine v2.0...
echo 🧠 Unified 25-Pillar Meta Research Super-Intelligence Stack
echo ------------------------------------------------------------

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.11+.
    exit /b 1
)

:: 2. Check and Setup Virtual Environment
if not exist "venv" (
    echo ⏳ Creating Virtual Environment...
    python -m venv venv
)
call venv\Scripts\activate

:: 3. Install/Update Dependencies
echo ⏳ Verifying Dependencies...
pip install -r backend/requirements.txt -q
if %errorlevel% neq 0 (
    echo ⚠️ Dependency installation encountered issues. Checking critical libs...
)

:: 4. Seed Database (Internal Quality)
echo ⏳ Seeding Persistent Collection...
python scripts/seed_db.py
if %errorlevel% neq 0 (
    echo ⚠️ Database seeding failed or already complete.
)

:: 5. Verify Model Infrastructure
echo ⏳ Checking Model Infrastructure...
if not exist "backend\ai_models" mkdir "backend\ai_models"
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\data" mkdir "backend\data"

:: 5. Launch Backend
echo 🚀 Launching Backend API (Port 8000)...
start /B python backend/main.py

:: 6. Wait for Backend Heartbeat
echo ⏳ Waiting for API heartbeat...
:heartbeat
timeout /t 2 /nobreak >nul
powershell -command "try { $r = Invoke-WebRequest -Uri http://localhost:8000/api/health; if($r.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }"
if %errorlevel% neq 0 (
    echo ⏳ API still starting...
    goto heartbeat
)
echo ✅ Backend Online.

:: 7. Launch Frontend
echo 🚀 Launching React Frontend...
cd frontend
if not exist "node_modules" (
    echo ⏳ Installing Node modules...
    npm install -q
)
start /B npm run dev

echo ------------------------------------------------------------
echo ✨ AetherStore Engine is now active!
echo 🌐 Frontend: http://localhost:5173
echo 🧠 AI Center: http://localhost:8000/static/super_intelligence_demo.html
echo 📖 API Docs: http://localhost:8000/docs
echo ------------------------------------------------------------
echo Press Ctrl+C to terminate both servers.
pause
