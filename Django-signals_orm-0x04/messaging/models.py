from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    last_edited = models.DateTimeField(null=True, blank=True)
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    is_thread_starter = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"

    def save(self, *args, **kwargs):
        # Automatically set is_thread_starter based on parent_message
        if self.parent_message is None:
            self.is_thread_starter = True
        super().save(*args, **kwargs)

    def get_thread(self):
        """
        Returns the entire thread of messages including all replies
        """
        messages = []
        if self.is_thread_starter:
            messages = Message.objects.filter(
                models.Q(pk=self.pk) |
                models.Q(parent_message=self)
            ).select_related(
                'sender',
                'receiver',
                'parent_message'
            ).prefetch_related(
                'replies'
            ).order_by('timestamp')
        return messages

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['parent_message']),
            models.Index(fields=['is_thread_starter']),
        ]

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    edited_at = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"History for message {self.message.id} (edited at {self.edited_at})"

    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message Histories'

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"

    class Meta:
        ordering = ['-created_at']