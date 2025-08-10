from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from django.core.mail import send_mail

from .models import User


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created: bool, **kwargs):
    if created:
        # Placeholder: enqueue a Celery task to send welcome email in production
        subject = "Welcome to AgroSphere"
        message = f"Hi {instance.get_full_name() or instance.email}, welcome to AgroSphere!"
        # In prod, use celery task, here we call send_mail for example:
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
        except Exception:
            # Logging in production
            pass
