from django.core.mail import send_mail


def send(user_email):

    send_mail(
        'You subscribed on mailing',
        'We will be send you spam notifications',
        'my_email',
        [user_email],
        fail_silently=False,
        )