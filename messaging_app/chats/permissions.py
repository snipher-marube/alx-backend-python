from rest_framework.permissions import BasePermission

class IsParticipant(BasePermission):
    # check is the user is a participant
    def has_object_permission(self, request, view, obj):
        # for conversational model
        if hasattr(obj, 'participants'):
            return obj.participants.filter(user_id=request.user.user_id).exists()
        
        # for message
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(user_id=request.user.user_id).exists()

        return False
    
class IsMessageSenderOrParticipant(BasePermission):
    # check if the user is a sender or a participant
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'sender') and hasattr(obj, 'conversation'):
            return (obj.sender.user_id==request.user.user_id or
                    obj.conversation.participants.filter(user_id=request.user.user_id).exists())
        
        return False