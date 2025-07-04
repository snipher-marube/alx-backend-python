from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
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
            'phone_number',
            'profile_picture',
            'bio',
            'last_active',
            'online_status',
            'created_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'last_active']
        extra_kwargs = {
            'profile_picture': {'required': False},
            'bio': {'required': False},
            'phone_number': {'required': False}
        }

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.user_id)
        token['username'] = user.username
        return token

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
    
    def validate_message_body(self, value):
        if not value.strip():
            raise serializers.ValidationError(_("Message cannot be empty"))
        if len(value) > 2000:
            raise serializers.ValidationError(_("Message is too long (max 2000 characters)"))
        return value

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

    name = serializers.CharField(
        max_length=100,
        required=False,
        allow_null=True,
        help_text="Name of the conversation (required for group chats)"
    )

    def validate_name(self, value):
        if self.initial_data.get('is_group_chat') and not value:
            raise serializers.ValidationError(_("Group chats must have a name"))
        if value and len(value) > 100:
            raise serializers.ValidationError(_("Name is too long (max 100 characters)"))
        return value

class ConversationCreateSerializer(serializers.ModelSerializer):
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
    
    def validate_participant_ids(self, value):
        if len(value) < 1:
            raise serializers.ValidationError(_("You must specify at least one participant"))
        
        existing_users = User.objects.filter(user_id__in=value).count()
        if existing_users != len(value):
            raise serializers.ValidationError(_("One or more participants do not exist"))
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        conversation = Conversation.objects.create(**validated_data)
        participants = User.objects.filter(user_id__in=participant_ids)
        conversation.participants.add(*participants)
        current_user = self.context['request'].user
        if current_user not in conversation.participants.all():
            conversation.participants.add(current_user)
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
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)