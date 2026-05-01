import os
from celery import Celery

# Fetch Redis URL from environment or use a safe local default
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "aetherstore_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    worker_concurrency=2, # Limit heavy 3D processing tasks
)

if __name__ == '__main__':
    celery_app.start()