import os


import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itmagazine.settings')

app = Celery('itmagazine')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


""" Sending every 4 minutes email spam """
app.conf.beat_schedule = {
    'send-spam-every-3-minutes': {
        'task': 'core.tasks.send_beat_emails',      # task registration
        'schedule': crontab(minute='*/3'),          # how often will be send spam
    },
}