from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Conversation, Message
from .serializers import (
    ConversationSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer
)
from django.db.models import Q

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only conversations where the current user is a participant
        """
        return self.queryset.filter(participants=self.request.user).order_by('-updated_at')

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'create':
            return ConversationCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """
        Automatically add the current user to the conversation participants
        """
        conversation = serializer.save()
        if self.request.user not in conversation.participants.all():
            conversation.participants.add(self.request.user)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """
        Custom endpoint to get messages for a specific conversation
        """
        conversation = self.get_object()
        if request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )

        messages = conversation.messages.all().order_by('sent_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return only messages from conversations where the current user is a participant
        """
        return self.queryset.filter(
            Q(conversation__participants=self.request.user) |
            Q(sender=self.request.user)
        ).distinct().order_by('-sent_at')

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'create':
            return MessageCreateSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        """
        Automatically set the sender to the current user
        """
        conversation = serializer.validated_data['conversation']
        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant in this conversation"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Custom create to handle the response format
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            MessageSerializer(instance=serializer.instance).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )