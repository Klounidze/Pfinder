from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    """Профиль пользователя — расширение стандартной модели User."""

    SERVICE_TYPES = [
        ('medicine', _('Медицина')),
        ('home', _('Дом')),
        ('education', _('Образование')),
        ('children', _('Дети')),
        ('construction', _('Строительство')),
        ('handmade', _('Хендмейд')),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name=_('Пользователь')
    )
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)
    service_type = models.CharField(
        _('Тип услуги'), max_length=20,
        choices=SERVICE_TYPES, blank=True
    )
    country = models.CharField(_('Страна'), max_length=100, blank=True)
    city = models.CharField(_('Город'), max_length=100, blank=True)
    bio = models.TextField(_('О себе'), blank=True, max_length=1000)
    avatar = models.ImageField(
        _('Аватар'), upload_to='avatars/', blank=True, null=True
    )
    is_provider = models.BooleanField(_('Исполнитель'), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Профиль')
        verbose_name_plural = _('Профили')

    def __str__(self):
        return f'Профиль {self.user.username}'

    @property
    def first_letter(self):
        return self.user.username[:1].upper()


class PortfolioImage(models.Model):
    """Фото портфолио исполнителя."""
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE,
        related_name='portfolio', verbose_name=_('Профиль')
    )
    image = models.ImageField(_('Изображение'), upload_to='portfolio/')
    caption = models.CharField(_('Подпись'), max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Фото портфолио')
        verbose_name_plural = _('Фото портфолио')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.profile.user.username} — {self.caption or "фото"}'


# ============ СИГНАЛЫ ============
@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """Создаёт профиль автоматически при регистрации."""
    if created:
        Profile.objects.create(user=instance)
    else:
        # На случай, если профиль не был создан
        Profile.objects.get_or_create(user=instance)