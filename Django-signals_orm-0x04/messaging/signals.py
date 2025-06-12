from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import Message, MessageHistory, Notification
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """
    Track message edits and save previous version to history
    """
    if instance.pk:  # Only for existing messages
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content changed
                # Get the user who made the edit (you might need to adapt this based on your auth system)
                editor = User.objects.filter(pk=instance.sender.pk).first()
                
                MessageHistory.objects.create(
                    message=old_message,
                    old_content=old_message.content,
                    edited_by=editor
                )
                instance.edited = True
                instance.last_edited = timezone.now()
        except Message.DoesNotExist:
            pass  # New message, no history to track

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

@receiver(post_delete, sender=User)
def cleanup_user_data(sender, instance, **kwargs):
    """
    Clean up all related data when a user is deleted.
    Explicitly handles deletion of messages, notifications, and updates message history.
    """
    # Delete all messages where user is either sender or receiver
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
    
    # For messages where this user edited them, set edited_by to None
    MessageHistory.objects.filter(edited_by=instance).update(edited_by=None)
    
    