"""Celery application setup"""

from celery import Celery
from helpers.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "supportrag_ai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["tasks"])

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)