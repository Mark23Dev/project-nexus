import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrosphere.settings.production')  # or your env

app = Celery('agrosphere')

# Read config from Django settings, prefixed with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all apps
app.autodiscover_tasks()
