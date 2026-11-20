from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.notification.registry import EVENTS


def send(notification):
    spec = EVENTS[notification.type]
    # one line: a newline in a subject is an error in Django's mail layer
    subject = " ".join(spec.subject(notification.payload).split())
    send_mail(
        subject=subject,
        message=f"{notification.title}\n\n{notification.body}",
        from_email=None,  # DEFAULT_FROM_EMAIL
        recipient_list=[notification.recipient.email],
        html_message=render_to_string(
            "email/notification_email.html",
            {"notification": notification, "frontend_url": settings.FRONTEND_BASE_URL},
        ),
    )
