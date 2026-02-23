# Docker Setup Guide - Aetherstore Engine

## 🐳 Quick Start with Docker

This guide will help you run the entire Aetherstore Engine stack using Docker Desktop.

## Prerequisites

1. **Docker Desktop** installed and running
   - Download from: https://www.docker.com/products/docker-desktop
   - Make sure it's running (you'll see the Docker icon in your system tray)

2. **Git** (optional, if cloning the repo)

## 🚀 Quick Start

### 1. Start Everything

```bash
# From the project root directory
docker-compose up
```

This will:
- Build the backend (Python 3.11) and frontend (Node 18) containers
- Start both services
- Backend available at: http://localhost:8000
- Frontend available at: http://localhost:8080

### 2. View Logs

```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### 3. Stop Everything

```bash
docker-compose down
```

### 4. Rebuild After Code Changes

```bash
# Rebuild and restart
docker-compose up --build

# Or rebuild specific service
docker-compose build backend
docker-compose up
```

## 📁 Project Structure

```
3D fashion store/
├── docker-compose.yml          # Main orchestration file
├── backend/
│   ├── Dockerfile              # Backend container definition
│   └── .dockerignore
├── frontend/
│   ├── Dockerfile              # Frontend dev container
│   ├── Dockerfile.prod         # Frontend production container
│   └── .dockerignore
└── DOCKER_SETUP.md            # This file
```

## 🔧 Development Workflow

### Hot Reload

Both services support hot reload:
- **Backend**: Code changes in `backend/` are reflected immediately (volume mounted)
- **Frontend**: Webpack dev server watches for changes and auto-reloads

### Making Changes

1. Edit code in your local files
2. Changes are automatically reflected in containers (via volumes)
3. Frontend webpack will rebuild automatically
4. Backend will reload if using `uvicorn --reload` (can be added to Dockerfile)

## 🎯 Service URLs

Once running:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (FastAPI Swagger)
- **Health Check**: http://localhost:8000/health

## 🗄️ Database Options

### Option 1: SQLite (Default - Easiest)

Already configured! No setup needed. Database file is stored in the container.

### Option 2: PostgreSQL (Production-like)

1. Uncomment the `postgres` service in `docker-compose.yml`
2. Update `DATABASE_URL` in backend environment:
   ```yaml
   environment:
     - DATABASE_URL=postgresql://aetherstore:aetherstore_dev@postgres:5432/aetherstore
   ```
3. Restart: `docker-compose up`

## 🏗️ Production Build

### Build Production Frontend

```bash
cd frontend
docker build -f Dockerfile.prod -t aetherstore-frontend:prod .
docker run -p 80:80 aetherstore-frontend:prod
```

### Build Production Backend

```bash
cd backend
docker build -t aetherstore-backend:prod .
docker run -p 8000:8000 aetherstore-backend:prod
```

## 🐛 Troubleshooting

### Port Already in Use

If ports 8000 or 8080 are already in use:

```yaml
# In docker-compose.yml, change:
ports:
  - "8001:8000"  # Use 8001 instead of 8000
  - "8081:8080"  # Use 8081 instead of 8080
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Database Issues

```bash
# Reset database (SQLite)
docker-compose exec backend rm aetherstore.db

# Or restart backend
docker-compose restart backend
```

### Frontend Build Errors

```bash
# Clear node_modules and rebuild
docker-compose exec frontend rm -rf node_modules
docker-compose exec frontend npm install
docker-compose restart frontend
```

### View Container Shell

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## 📊 Resource Usage

Typical resource usage:
- **Backend**: ~200-300 MB RAM
- **Frontend**: ~100-200 MB RAM
- **Total**: ~400-500 MB RAM

Adjust in Docker Desktop settings if needed.

## 🔐 Environment Variables

Edit `docker-compose.yml` to set environment variables:

```yaml
environment:
  - DATABASE_URL=sqlite:///./aetherstore.db
  - DEBUG=True
  - SECRET_KEY=your-secret-key
  - STRIPE_SECRET_KEY=your-stripe-key
  # ... etc
```

Or use a `.env` file (create `backend/.env` and reference it in docker-compose.yml).

## 🚢 Deployment

For production deployment:

1. Use `Dockerfile.prod` for frontend
2. Set `DEBUG=False` in backend
3. Use PostgreSQL instead of SQLite
4. Add proper secrets management
5. Use Docker Swarm or Kubernetes for orchestration

## 📚 Next Steps

1. **Start the services**: `docker-compose up`
2. **Open frontend**: http://localhost:8080
3. **Test API**: http://localhost:8000/docs
4. **Check health**: http://localhost:8000/health

## 💡 Tips

- Use `docker-compose up -d` to run in background
- Use `docker-compose ps` to see running containers
- Use `docker-compose stop` to stop without removing
- Use `docker-compose down -v` to remove volumes too

Happy coding! 🎉

