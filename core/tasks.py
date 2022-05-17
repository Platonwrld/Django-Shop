from django.core.mail import send_mail
from itmagazine.celery import app
from .service import * 
from .models import *


""" Function that will be launch in Celery """
@app.task       # decorator that tell celery that this task need in launch
def send_spam_email(user_email):

    send(user_email)


@app.task
def send_beat_emails():
    # некая итерация по всем объектам модели Контакты
    emails = list(Contact.objects.values_list('email', flat=True))
    for contact in emails:
        print(contact)
        send_mail(
            'Hello',
            'This is simple spam every 3 minutes with Celery help',
            'my_email',
            [contact],    # мол, одна пачка
            fail_silently=False,
        )