from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .models import Message


@login_required
def inbox(request):
    """Список диалогов."""
    # Находим всех собеседников
    sent_to = Message.objects.filter(sender=request.user) \
        .values_list('receiver', flat=True).distinct()
    received_from = Message.objects.filter(receiver=request.user) \
        .values_list('sender', flat=True).distinct()
    user_ids = set(list(sent_to) + list(received_from))
    users = User.objects.filter(id__in=user_ids)

    dialogs = []
    for u in users:
        last_msg = Message.get_dialog(request.user, u).last()
        unread = Message.objects.filter(sender=u, receiver=request.user, is_read=False).count()
        if last_msg:
            dialogs.append({
                'user': u,
                'last_message': last_msg,
                'unread': unread,
            })
    dialogs.sort(key=lambda d: d['last_message'].created_at, reverse=True)

    return render(request, 'chat/inbox.html', {'dialogs': dialogs})


@login_required
def dialog(request, username):
    """Диалог с конкретным пользователем."""
    other = get_object_or_404(User, username=username)
    if other == request.user:
        return redirect('inbox')

    messages_qs = Message.get_dialog(request.user, other)

    # Помечаем входящие как прочитанные
    Message.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(
                sender=request.user,
                receiver=other,
                content=content,
            )
        return redirect('dialog', username=username)

    return render(request, 'chat/dialog.html', {
        'other': other,
        'messages_list': messages_qs,
    })


@login_required
@require_POST
def send_message_api(request):
    """API для отправки сообщения (AJAX)."""
    receiver_id = request.POST.get('receiver_id')
    content = request.POST.get('content', '').strip()
    if not receiver_id or not content:
        return JsonResponse({'success': False, 'error': _('Заполните все поля.')})

    receiver = get_object_or_404(User, pk=receiver_id)
    msg = Message.objects.create(
        sender=request.user,
        receiver=receiver,
        content=content,
    )
    return JsonResponse({
        'success': True,
        'message_id': msg.id,
        'created_at': msg.created_at.strftime('%H:%M'),
    })


@login_required
def get_messages_api(request, username):
    """API для получения списка сообщений в диалоге (для чата-модалки)."""
    other = get_object_or_404(User, username=username)
    msgs = Message.get_dialog(request.user, other)
    Message.objects.filter(sender=other, receiver=request.user, is_read=False).update(is_read=True)

    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'sender_id': m.sender.id,
        'content': m.content,
        'is_own': m.sender == request.user,
        'created_at': m.created_at.strftime('%d.%m.%Y %H:%M'),
    } for m in msgs]

    return JsonResponse({'success': True, 'messages': data})


@login_required
def mark_all_read_api(request):
    """Пометить все сообщения как прочитанные."""
    if request.method == 'POST':
        Message.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


@login_required
def notifications_count_api(request):
    """Количество непрочитанных сообщений."""
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'unread_count': count})


@login_required
def get_or_create_dialog(request, user_id):
    """Создаёт или возвращает диалог с пользователем (для кнопки «Написать»)."""
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        return redirect('inbox')
    return redirect('dialog', username=other.username)