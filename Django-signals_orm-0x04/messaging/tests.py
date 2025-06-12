from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class MessagingTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', password='testpass123')

    def test_message_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.receiver, self.user2)
        self.assertEqual(message.content, "Test message")
        self.assertFalse(message.is_read)

    def test_notification_auto_creation(self):
        message = Message.objects.create(
            sender=self.user1,
            receiver=self.user2,
            content="Test message"
        )
        
        # Check if notification was automatically created
        notification = Notification.objects.filter(user=self.user2, message=message).first()
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user2)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_multiple_messages_create_multiple_notifications(self):
        # Create 3 messages
        for i in range(3):
            Message.objects.create(
                sender=self.user1,
                receiver=self.user2,
                content=f"Test message {i}"
            )
        
        # Check if 3 notifications were created
        self.assertEqual(Notification.objects.filter(user=self.user2).count(), 3)