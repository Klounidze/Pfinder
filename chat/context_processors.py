from .models import Message


def unread_messages(request):
    """Добавляет в контекст всех шаблонов уведомления о новых сообщениях."""
    if request.user.is_authenticated:
        unread = Message.objects.filter(receiver=request.user, is_read=False)
        # Последние 10 уведомлений
        notifications_list = []
        seen_senders = set()
        for msg in unread.order_by('-created_at')[:10]:
            notifications_list.append({
                'id': msg.id,
                'sender_name': msg.sender.username,
                'sender_id': msg.sender.id,
                'other_user_id': msg.sender.id,
                'other_user_name': msg.sender.username,
                'content': msg.content[:80],
                'created_at': msg.created_at,
                'is_read': msg.is_read,
            })
        return {
            'unread_count': unread.count(),
            'notifications_list': notifications_list,
        }
    return {'unread_count': 0, 'notifications_list': []}