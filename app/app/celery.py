import os
from datetime import timedelta

from celery import Celery
from kombu import Queue, Exchange
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery("app")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.task_queues = [
    Queue('tasks', Exchange('tasks'), routing_key='tasks',
          queue_arguments={'x-max-priority': 10}),
]

app.conf.task_acks_late = True
app.conf.task_default_priority = 5
app.conf.worker_prefetch_multiplier = 1
app.conf.worker_concurrency = 1

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'my-task': {
        'task': 'core.tasks.send_daily_reminders',
        'schedule': timedelta(minutes=15),
    },
    'task-2': {
        'task': "core.tasks.send_priority_tasks",
        'schedule': timedelta(minutes=60),
    }
}
