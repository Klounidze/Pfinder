from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Message(models.Model):
    """Личное сообщение между пользователями."""

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='sent_messages', verbose_name=_('Отправитель')
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_messages', verbose_name=_('Получатель')
    )
    content = models.TextField(_('Сообщение'), max_length=2000)
    is_read = models.BooleanField(_('Прочитано'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Сообщение')
        verbose_name_plural = _('Сообщения')
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username}: {self.content[:30]}'

    @staticmethod
    def get_dialog(user1, user2):
        """Все сообщения между двумя пользователями."""
        return Message.objects.filter(
            models.Q(sender=user1, receiver=user2) |
            models.Q(sender=user2, receiver=user1)
        ).order_by('created_at')

    @staticmethod
    def unread_count_for(user):
        return Message.objects.filter(receiver=user, is_read=False).count()