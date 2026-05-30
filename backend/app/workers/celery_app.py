from celery import Celery
from app.config import settings

celery_app = Celery(
    "caseflow",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="America/Chicago",
    enable_utc=True,
    beat_schedule={
        "drive-ingestion": {
            "task": "app.workers.tasks.run_drive_ingestion_task",
            "schedule": 90.0,  # every 90 seconds
        },
        "gmail-ingestion": {
            "task": "app.workers.tasks.run_gmail_ingestion_task",
            "schedule": 120.0,
        },
    },
)
