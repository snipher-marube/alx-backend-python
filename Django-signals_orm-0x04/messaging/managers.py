from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """
    Custom manager for unread messages with optimized queries
    """
    def unread_for_user(self, user):
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related(
            'sender'
        ).only(
            'id',
            'content',
            'timestamp',
            'sender__username',
            'sender__id'
        ).order_by('-timestamp')