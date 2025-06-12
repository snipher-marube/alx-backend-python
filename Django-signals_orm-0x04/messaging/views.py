from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.db.models import Q
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def message_list(request):
    """
    View to display all conversations for the current user, optimized with select_related
    """
    # Get all messages where user is either sender or receiver
    user_messages = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related(
        'sender',
        'receiver',
        'parent_message'
    ).prefetch_related(
        'replies'
    ).order_by('-timestamp')

    # Group by thread starters
    threads = [msg for msg in user_messages if msg.is_thread_starter]

    return render(request, 'messaging/message_list.html', {
        'threads': threads
    })

@login_required
def message_thread(request, message_id):
    """
    View to display a complete message thread with all replies
    Uses recursive querying through the ORM
    """
    # Get the base message with all related data
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver', 'parent_message'),
        pk=message_id,
        is_thread_starter=True
    )

    # Get the entire thread with optimized queries
    thread = Message.objects.filter(
        Q(pk=message_id) | Q(parent_message=message_id)
    ).select_related(
        'sender',
        'receiver'
    ).order_by('timestamp')

    return render(request, 'messaging/message_thread.html', {
        'thread': thread,
        'main_message': message
    })

@login_required
@require_POST
def send_message(request):
    """
    View to handle sending new messages and replies
    """
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        try:
            receiver = User.objects.get(pk=receiver_id)
            parent_message = None
            if parent_id:
                parent_message = Message.objects.get(pk=parent_id)

            message = Message.objects.create(
                sender=request.user,
                receiver=receiver,
                content=content,
                parent_message=parent_message
            )

            messages.success(request, 'Message sent successfully!')
            return redirect('message_thread', message_id=message.id if message.is_thread_starter else message.parent_message.id)

        except User.DoesNotExist:
            messages.error(request, 'Recipient not found')
        except Message.DoesNotExist:
            messages.error(request, 'Parent message not found')

    return redirect('message_list')

@login_required
@require_POST
def delete_user(request):
    """
    View to handle user account deletion with confirmation.
    """
    if request.method == 'POST':
        user = request.user
        logout(request)  # Logout before deletion to avoid issues
        user.delete()
        messages.success(request, 'Your account has been successfully deleted.')
        return redirect('home')
    


@login_required
def inbox(request):
    """
    View to display unread messages in user's inbox
    Uses custom manager with optimized query
    """
    unread_messages = Message.unread.unread_for_user(request.user)
    
    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages
    })

@login_required
def mark_as_read(request, message_id):
    """
    View to mark a message as read
    """
    message = Message.objects.filter(
        receiver=request.user,
        id=message_id
    ).first()
    
    if message:
        message.is_read = True
        message.save(update_fields=['is_read'])
        messages.success(request, "Message marked as read")
    else:
        messages.error(request, "Message not found")
    
    return redirect('inbox')

@login_required
def message_detail(request, message_id):
    """
    View to display a single message and mark it as read
    """
    message = Message.objects.filter(
        receiver=request.user,
        id=message_id
    ).select_related(
        'sender'
    ).only(
        'id',
        'content',
        'timestamp',
        'sender__username',
        'is_read'
    ).first()
    
    if not message:
        messages.error(request, "Message not found")
        return redirect('inbox')
    
    # Mark as read when viewed
    if not message.is_read:
        message.is_read = True
        message.save(update_fields=['is_read'])
    
    return render(request, 'messaging/message_detail.html', {
        'message': message
    })