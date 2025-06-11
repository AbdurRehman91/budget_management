import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "budget_management.settings")

app = Celery("budget_management")

app.config_from_object("django.conf:settings", namespace="CELERY")

# Set the broker URL to Redis
app.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

app.autodiscover_tasks()
