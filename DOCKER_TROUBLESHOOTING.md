# Docker Troubleshooting Guide

## Network Timeout Issues

If you're seeing `ReadTimeoutError` when building the backend container:

### Quick Fixes:

1. **Retry the build** - Sometimes it's just a temporary network issue:
   ```bash
   docker-compose build backend
   ```

2. **Check your internet connection** - Large packages like TensorFlow/PyTorch need stable connection

3. **Use a faster network** - If on WiFi, try wired connection

4. **Build during off-peak hours** - PyPI can be slow during peak times

### Alternative: Install Dependencies in Stages

If timeouts persist, we can split the requirements into smaller chunks. Let me know if you want this approach.

### Alternative: Use Pre-built Base Image

We could create a base image with dependencies pre-installed. This is useful if you rebuild frequently.

## Other Common Issues

### Port Already in Use

```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# Kill the process or change ports in docker-compose.yml
```

### Out of Disk Space

```bash
# Clean up Docker
docker system prune -a
docker volume prune
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

## Still Having Issues?

1. Check Docker Desktop is running
2. Ensure you have enough disk space (Docker needs ~10GB)
3. Try restarting Docker Desktop
4. Check Windows Firewall isn't blocking Docker

