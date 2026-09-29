from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import ProviderService, Category, Review, Order
from .forms import ProviderServiceForm, ReviewForm
from accounts.models import Profile


def index(request):
    """Главная: поиск + список услуг."""
    services = ProviderService.objects.filter(is_active=True).select_related('user')

    # Фильтры
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    country = request.GET.get('country', '').strip()
    city = request.GET.get('city', '').strip()

    if q:
        services = services.filter(
            Q(title__icontains=q) |
            Q(description__icontains=q) |
            Q(city__icontains=q) |
            Q(country__icontains=q)
        )
    if category:
        services = services.filter(category=category)
    if country:
        services = services.filter(country__icontains=country)
    if city:
        services = services.filter(city__icontains=city)

    # Список стран/городов для селектов
    countries = ProviderService.objects.filter(is_active=True) \
        .values_list('country', flat=True).distinct().order_by('country')
    cities = ProviderService.objects.filter(is_active=True) \
        .values_list('city', flat=True).distinct().order_by('city')

    categories = Category.CATEGORY_CHOICES

    context = {
        'services': services,
        'categories': categories,
        'countries': countries,
        'cities': cities,
        'current_q': q,
        'current_category': category,
        'current_country': country,
        'current_city': city,
        'results_count': services.count(),
    }
    return render(request, 'index.html', context)


@login_required
def add_service(request):
    """Добавление услуги."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if not profile.is_provider:
        messages.warning(request, _('Сначала отметьте себя как исполнителя в профиле.'))
        return redirect('edit_profile')

    if request.method == 'POST':
        form = ProviderServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.user = request.user
            if not service.phone:
                service.phone = profile.phone
            service.save()
            messages.success(request, _('Услуга добавлена!'))
            return redirect('service_detail', pk=service.pk)
        else:
            messages.error(request, _('Проверьте правильность заполнения формы.'))
    else:
        form = ProviderServiceForm(initial={
            'country': profile.country,
            'city': profile.city,
            'phone': profile.phone,
            'category': profile.service_type,
        })
    return render(request, 'services/add_provider.html', {'form': form})


def service_detail(request, pk):
    """Детали услуги + отзывы + форма отзыва."""
    service = get_object_or_404(
        ProviderService.objects.select_related('user'),
        pk=pk
    )
    reviews = service.reviews.select_related('author').order_by('-created_at')

    # Право на отзыв: завершённый заказ и ещё нет отзыва от него
    can_review = False
    if request.user.is_authenticated and request.user != service.user:
        has_completed = Order.objects.filter(
            service=service, client=request.user, status='completed'
        ).exists()
        already_reviewed = Review.objects.filter(service=service, author=request.user).exists()
        can_review = has_completed and not already_reviewed

    if request.method == 'POST' and can_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.provider = service.user
            review.author = request.user
            review.save()
            messages.success(request, _('Спасибо за отзыв!'))
            return redirect('service_detail', pk=service.pk)
    else:
        form = ReviewForm()

    context = {
        'service': service,
        'reviews': reviews,
        'can_review': can_review,
        'review_form': form,
    }
    return render(request, 'services/provider_detail.html', context)


@login_required
def create_order(request, pk):
    """Создание заказа (для права на отзыв)."""
    service = get_object_or_404(ProviderService, pk=pk)
    if service.user == request.user:
        messages.error(request, _('Нельзя заказать собственную услугу.'))
        return redirect('service_detail', pk=pk)

    order, created = Order.objects.get_or_create(
        service=service, client=request.user,
        defaults={'status': 'pending'}
    )
    if created:
        messages.success(request, _('Заявка отправлена! После завершения услуги вы сможете оставить отзыв.'))
    else:
        messages.info(request, _('Заявка уже существует.'))
    return redirect('service_detail', pk=pk)


@login_required
def my_orders(request):
    """Мои заказы (как исполнителя и как клиента)."""
    as_client = Order.objects.filter(client=request.user).select_related('service')
    as_provider = Order.objects.filter(service__user=request.user).select_related('service', 'client')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, pk=order_id, service__user=request.user)
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == 'completed':
                order.completed_at = timezone.now()
            order.save()
            messages.success(request, _('Статус заказа обновлён.'))
        return redirect('my_orders')

    return render(request, 'services/my_orders.html', {
        'as_client': as_client,
        'as_provider': as_provider,
    })


def search_results(request):
    """Отдельная страница результатов поиска (по категории)."""
    return index(request)