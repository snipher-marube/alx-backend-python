from django.db.models import Q
from rest_framework import viewsets, status, filters, serializers
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from .permissions import IsParticipantOfConversation
from .filters import MessageFilter

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']

    def get_queryset(self):
        """Return only conversations where the current user is a participant"""
        return super().get_queryset().filter(participants=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return ConversationCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get', 'put', 'patch', 'delete'])
    def messages(self, request, pk=None):
        conversation = self.get_object()
        messages = conversation.messages.all().order_by('sent_at')
        
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            message_id = request.data.get('id')
            message = Message.objects.filter(
                id=message_id,
                conversation_id=conversation.id,
                sender=request.user
            ).first()
            
            if not message:
                return Response(
                    {"detail": "Message not found or not owned by user"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            if request.method == 'DELETE':
                message.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                serializer = MessageSerializer(message, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [filters.OrderingFilter]
    filterset_class = MessageFilter
    ordering_fields = ['sent_at']
    ordering = ['-sent_at']

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(conversation__participants=self.request.user) |
            Q(sender=self.request.user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise serializers.ValidationError("Not a participant")
        serializer.save(sender=self.request.user)