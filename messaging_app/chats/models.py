from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
import uuid

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)

        if not extra_fields.get('username'):
            base_username = email.split('@')[0]
            username = slugify(base_username.replace('.', '_'))
            counter = 1
            while self.model.objects.filter(username=username).exists():
                username = f"{slugify(base_username.replace('.', '_'))}_{counter}"
                counter += 1
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class OnlineStatus(models.TextChoices):
        ONLINE = 'ONLINE', _("Online")
        OFFLINE = 'OFFLINE', _("Offline")
    
    # Using UUID as primary key instead of BigAutoField
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=255,
        verbose_name=_('username'),
        unique=True,
        null=True,
        blank=True,
        help_text=_('username will automatically be generated from the email')
    )
    phone_number = PhoneNumberField(
        unique=True,
        verbose_name=_('Phone Number')
    )
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(blank=True)
    last_active = models.DateTimeField(auto_now=True)
    online_status = models.CharField(
        max_length=15,
        choices=OnlineStatus.choices,
        default=OnlineStatus.OFFLINE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def _generate_username(self):
        base_username = self.email.split('@')[0]
        return slugify(base_username.replace('.', '_'))

    def save(self, *args, **kwargs):
        if not self.username:
            base = self._generate_username()
            self.username = base
            counter = 1
            while User.objects.filter(username=self.username).exists():
                self.username = f"{base}_{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.get_full_name()}"

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group_chat and self.name:
            return self.name
        usernames = [user.username for user in self.participants.all()]
        return f"Conversation between {', '.join(usernames)}"

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender.get_full_name()} at {self.timestamp}"