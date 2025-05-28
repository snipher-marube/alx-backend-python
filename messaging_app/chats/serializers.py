from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, Conversation, Message

class UserSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField()

    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'first_name',
            'last_name',
            'profile_picture',
            'bio',
            'last_active',
            'online_status',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'last_active']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'bio': {'required': False}
        }

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'sender',
            'message_body',
            'sent_at',
            'edited',
            'read',
            'deleted'
        ]
        read_only_fields = ['message_id', 'sent_at', 'sender']
    
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participants',
            'created_at',
            'updated_at',
            'is_group_chat',
            'messages',
            'name',
            'last_message',
        ]
        read_only_fields = ['conversation_id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-sent_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

class ConversationCreateSearializer(serializers.ModelSerializer):
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Conversation
        fields = [
            'conversation_id',
            'participant_ids',
            'is_group_chat',
            'name',
        ]
        read_only_fields = ['conversation_id']
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)

        # Add participant to the conversation
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.add(*participants)
        return conversation
    
class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'message_id',
            'conversation',
            'message_body'
        ]
        read_only_fields = ['message_id']

        def create(self, validated_data):
            # Automatically set the sender to the current user
            validated_data['sender'] = self.context['request'].user
            return super().create(validated_data)
