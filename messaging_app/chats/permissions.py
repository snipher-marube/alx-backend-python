from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import permissions

class IsParticipantOfConversation(IsAuthenticated):
    """
    Custom permission to only allow participants of a conversation to access it.
    Handles both Conversation and Message models.
    """
    
    def has_object_permission(self, request, view, obj):
        # First check if user is authenticated (handled by IsAuthenticated)
        if not super().has_permission(request, view):
            return False

        # Handle Conversation model
        if hasattr(obj, 'participants'):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # Handle Message model
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()
        
        return False