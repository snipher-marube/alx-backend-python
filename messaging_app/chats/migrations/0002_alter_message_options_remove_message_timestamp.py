# Generated by Django 5.2 on 2025-05-28 10:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ['sent_at']},
        ),
        migrations.RemoveField(
            model_name='message',
            name='timestamp',
        ),
    ]
