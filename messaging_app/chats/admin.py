from django.contrib import admin
from .models import User, Conversation, Message

class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'email', 'phone_number', 'is_active', 'last_active', 'online_status')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')
    list_filter = ('is_active', 'online_status')
    readonly_fields = ('user_id', 'created_at', 'last_active')

class ConversationAdmin(admin.ModelAdmin):
    list_display = ('conversation_id', 'name', 'is_group_chat', 'created_at', 'updated_at')
    search_fields = ('name', 'participants__username')
    list_filter = ('is_group_chat',)
    filter_horizontal = ('participants',)
    readonly_fields = ('conversation_id', 'created_at', 'updated_at')

    def get_participants(self, obj):
        return ", ".join([user.username for user in obj.participants.all()])
    get_participants.short_description = 'Participants'

class MessageAdmin(admin.ModelAdmin):
    list_display = ('message_id', 'get_conversation', 'get_sender', 'sent_at', 'read', 'edited', 'deleted')
    search_fields = ('message_body', 'sender__username', 'conversation__name')
    list_filter = ('read', 'edited', 'deleted', 'sent_at')
    readonly_fields = ('message_id', 'sent_at')

    def get_conversation(self, obj):
        return obj.conversation
    get_conversation.short_description = 'Conversation'

    def get_sender(self, obj):
        return obj.sender.username
    get_sender.short_description = 'Sender'

admin.site.register(User, UserAdmin)
admin.site.register(Conversation, ConversationAdmin)
admin.site.register(Message, MessageAdmin)