# chatApplication/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatApplication.settings')

app = Celery('chatApplication')

# Read config from Django settings, use CELERY_ namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in installed apps
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'print-hello-every-day-17': {
        'task': 'chat.tasks.print_hello',
        'schedule': crontab(hour=12, minute=29),
    },
}

