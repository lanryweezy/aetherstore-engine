# Local Testing Guide

## 🐳 Recommended: Docker Setup

**For the easiest setup, use Docker Desktop!** See `DOCKER_SETUP.md` for complete instructions.

```bash
docker-compose up
```

This solves Python version issues and gives you a production-like environment.

---

## 💻 Manual Setup (Alternative)

If you prefer not to use Docker:

## Prerequisites

- Python 3.10 or 3.11 installed (3.13 has compatibility issues)
- Node.js 16+ and npm installed
- PostgreSQL installed (or use SQLite for quick testing)

## Quick Start

### Option 1: SQLite (Easiest - No Database Setup)

The app can run with SQLite for quick testing. Just start the services!

### Option 2: PostgreSQL (Production-like)

1. Install PostgreSQL
2. Create a database:
```sql
CREATE DATABASE aetherstore;
```

## Step-by-Step Setup

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (see below)
# Then run the server
python main_app.py
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

### 3. Environment Variables

Create `backend/.env` file:

```env
# Database
DATABASE_URL=sqlite:///./aetherstore.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/aetherstore

# App Settings
APP_NAME=Aetherstore Engine
APP_VERSION=1.0.0
DEBUG=True
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
CORS_CREDENTIALS=True
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_HEADERS=*

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment (Optional for testing)
STRIPE_SECRET_KEY=
STRIPE_PUBLIC_KEY=
PAYSTACK_SECRET_KEY=
PAYSTACK_PUBLIC_KEY=
STRIPE_WEBHOOK_SECRET=

# Email (Optional for testing)
EMAIL_PROVIDER=sendgrid
EMAIL_SENDGRID_API_KEY=
EMAIL_MAILGUN_API_KEY=
EMAIL_MAILGUN_DOMAIN=
FROM_EMAIL=noreply@aetherstore.engine
FROM_NAME=Aetherstore Engine

# Monitoring (Optional)
SENTRY_DSN=
```

## Testing the Application

### Backend Health Check

Once backend is running (default: http://localhost:8000):

```bash
# Check health
curl http://localhost:8000/health

# Check API info
curl http://localhost:8000/api/info
```

### Frontend

Frontend will be available at: http://localhost:3000 (or port shown in terminal)

### Test Endpoints

1. **Health Check**: http://localhost:8000/health
2. **API Info**: http://localhost:8000/api/info
3. **Metrics**: http://localhost:8000/api/metrics
4. **Frontend**: http://localhost:3000

## Troubleshooting

### Backend Issues

**Database connection error:**
- Check DATABASE_URL in .env
- For SQLite: Ensure write permissions
- For PostgreSQL: Check database exists and credentials

**Import errors:**
- Make sure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**Port already in use:**
- Change port in `main_app.py` or kill process using port 8000

### Frontend Issues

**Tailwind not working:**
- Run `npm install` again
- Check `postcss.config.js` exists
- Clear cache and rebuild

**Module not found:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

**Port conflict:**
- Webpack dev server will auto-find next available port
- Or change port in `webpack.config.js`

## Quick Test Commands

```bash
# Test backend
cd backend
python main_app.py

# Test frontend (in new terminal)
cd frontend
npm start

# Run both (if you have a process manager)
# Install concurrently: npm install -g concurrently
concurrently "cd backend && python main_app.py" "cd frontend && npm start"
```

## Expected Output

### Backend:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Database initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend:
```
webpack compiled successfully
App running at http://localhost:3000
```

## Next Steps

1. Open http://localhost:3000 in browser
2. Check browser console for errors
3. Test API endpoints via http://localhost:8000/docs (FastAPI auto-docs)
4. Try the futuristic UI components!

