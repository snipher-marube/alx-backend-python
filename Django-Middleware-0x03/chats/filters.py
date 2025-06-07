import django_filters
from django.db.models import Q
from .models import Message

class MessageFilter(django_filters.FilterSet):
    conversation = django_filters.UUIDFilter(field_name='conversation__conversation_id')
    sender = django_filters.UUIDFilter(field_name='sender__user_id')
    start_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Message
        fields =['conversation', 'sent_at', 'sender', 'read']

    
    def filter_search(self, queryset, name , value):
        return queryset.filter(
            Q(message_body__icontains=value),
            Q(sender__username__icontains=value),
            Q(sender__email__icontains=value),
        )