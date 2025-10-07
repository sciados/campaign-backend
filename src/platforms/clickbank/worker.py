# worker.py
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery.conf.beat_schedule = {
    "sync-clickbank-sales-nightly": {
        "task": "tasks.sync_clickbank_sales",
        "schedule": 60 * 60 * 24,  # every 24 hours
    },
}
