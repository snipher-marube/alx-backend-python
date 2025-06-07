from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework import permissions

class IsParticipantOfConversation(IsAuthenticated):
    """
    Custom permission to only allow participants of a conversation to access it.
    Handles both Conversation and Message models.
    """
    
    def has_permission(self, request, view):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            return False
        
        # For list/create actions, rely on get_queryset filtering
        if view.action in ['list', 'create']:
            return True
            
        return super().has_permission(request, view)
    
    def has_object_permission(self, request, view, obj):
        # Handle Conversation model
        if hasattr(obj, 'participants'):
            return obj.participants.filter(id=request.user.id).exists()
        
        # Handle Message model
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        
        return False