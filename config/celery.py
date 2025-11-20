import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Lê configurações CELERY_* do settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descobrir tasks.py nos apps
app.autodiscover_tasks()