from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message, Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    Creates a notification for the receiver when a new message is received.
    """
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance,
            is_read=False
        )