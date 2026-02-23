# 🚀 Quick Start - Aetherstore Engine

## Option 1: Docker (Recommended) ⭐

**Best for:** Easy setup, no Python version issues, production-like environment

### Steps:

1. **Make sure Docker Desktop is running**

2. **Start everything:**
   ```bash
   docker-compose up
   ```

3. **Open in browser:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

4. **Stop when done:**
   ```bash
   docker-compose down
   ```

That's it! 🎉

See `DOCKER_SETUP.md` for more details.

---

## Option 2: Manual Setup

**Best for:** Direct control, faster iteration (if you have Python 3.10/3.11)

### Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
python main_app.py
```

### Frontend:

```bash
cd frontend
npm install
npm start
```

See `LOCAL_TESTING.md` for complete manual setup guide.

---

## 🎯 Which Should You Use?

- **Use Docker if:** You want it to "just work", have Python 3.13, or want production-like setup
- **Use Manual if:** You have Python 3.10/3.11, want faster hot-reload, or prefer direct control

Both work great! Docker is just easier to get started. 😊

