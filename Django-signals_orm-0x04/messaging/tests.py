from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory
from django.utils import timezone

User = get_user_model()

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_edit_history(self):
        # Create initial message
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Original message"
        )
        
        # Edit the message
        message.content = "Edited message"
        message.save()
        
        # Check if history was created
        history = MessageHistory.objects.filter(message=message).first()
        self.assertIsNotNone(history)
        self.assertEqual(history.old_content, "Original message")
        self.assertEqual(history.edited_by, self.user1)
        
        # Check message flags were updated
        message.refresh_from_db()
        self.assertTrue(message.edited)
        self.assertIsNotNone(message.last_edited)

    def test_multiple_edits_create_multiple_history_records(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="First version"
        )
        
        # First edit
        message.content = "Second version"
        message.save()
        
        # Second edit
        message.content = "Third version"
        message.save()
        
        # Check history count
        self.assertEqual(MessageHistory.objects.filter(message=message).count(), 2)
        
        # Check history content
        history = MessageHistory.objects.filter(message=message).order_by('edited_at')
        self.assertEqual(history[0].old_content, "First version")
        self.assertEqual(history[1].old_content, "Second version")