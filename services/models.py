from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """Категория услуги (фиксированный набор + возможность расширения)."""

    CATEGORY_CHOICES = [
        ('medicine', _('Медицина')),
        ('home', _('Дом')),
        ('education', _('Образование')),
        ('children', _('Дети')),
        ('construction', _('Строительство')),
        ('handmade', _('Хендмейд')),
    ]

    slug = models.SlugField(_('Код'), max_length=50, unique=True, choices=CATEGORY_CHOICES)
    name_ru = models.CharField(_('Название (RU)'), max_length=100)
    name_en = models.CharField(_('Название (EN)'), max_length=100, blank=True)
    icon = models.CharField(_('Иконка (emoji)'), max_length=10, default='🛠️')

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def __str__(self):
        return self.name_ru

    @property
    def display_name(self):
        from django.utils import translation
        if translation.get_language() == 'en' and self.name_en:
            return self.name_en
        return self.name_ru


class ProviderService(models.Model):
    """Услуга, предлагаемая исполнителем."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='services', verbose_name=_('Исполнитель')
    )
    category = models.CharField(
        _('Категория'), max_length=50,
        choices=Category.CATEGORY_CHOICES
    )
    title = models.CharField(_('Название услуги'), max_length=200)
    description = models.TextField(_('Описание'), max_length=2000)
    price = models.DecimalField(
        _('Цена (₽)'), max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    price_unit = models.CharField(
        _('Единица'), max_length=50, blank=True,
        help_text=_('например: час, день, проект')
    )
    country = models.CharField(_('Страна'), max_length=100)
    city = models.CharField(_('Город'), max_length=100)
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)
    is_active = models.BooleanField(_('Активна'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Услуга')
        verbose_name_plural = _('Услуги')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.user.username}'

    @property
    def avg_rating(self):
        reviews = self.reviews.all()
        if not reviews.exists():
            return 0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

    @property
    def reviews_count(self):
        return self.reviews.count()

    def completed_orders(self):
        """Завершённые заказы (для права отзыва)."""
        return self.orders.filter(status='completed').count()


class Order(models.Model):
    """Заказ услуги — нужен для права оставить отзыв."""

    STATUS_CHOICES = [
        ('pending', _('Ожидает')),
        ('accepted', _('Принят')),
        ('completed', _('Завершён')),
        ('cancelled', _('Отменён')),
    ]

    service = models.ForeignKey(
        ProviderService, on_delete=models.CASCADE,
        related_name='orders', verbose_name=_('Услуга')
    )
    client = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='orders', verbose_name=_('Клиент')
    )
    status = models.CharField(
        _('Статус'), max_length=20,
        choices=STATUS_CHOICES, default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.pk} — {self.service.title}'


class Review(models.Model):
    """Отзыв. Можно оставить только после завершённого заказа."""

    service = models.ForeignKey(
        ProviderService, on_delete=models.CASCADE,
        related_name='reviews', verbose_name=_('Услуга'),
        null=True, blank=True
    )
    provider = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='received_reviews', verbose_name=_('Исполнитель')
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='written_reviews', verbose_name=_('Автор')
    )
    rating = models.PositiveSmallIntegerField(
        _('Оценка'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_('Комментарий'), max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']
        unique_together = ('service', 'author')  # один отзыв на услугу от пользователя

    def __str__(self):
        return f'Отзыв от {self.author.username} → {self.provider.username}'