from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

from .forms import RegisterForm, LoginForm, ProfileEditForm, PortfolioUploadForm
from .models import Profile, PortfolioImage
from services.models import Review, ProviderService


def register_view(request):
    """Регистрация пользователя."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Регистрация успешна! Добро пожаловать!'))
            return redirect('profile')
        else:
            messages.error(request, _('Пожалуйста, исправьте ошибки в форме.'))
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Вход пользователя."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, _('Вы вошли в систему.'))
                return redirect('profile')
        messages.error(request, _('Неверный логин или пароль.'))
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Выход."""
    logout(request)
    messages.info(request, _('Вы вышли из системы.'))
    return redirect('index')


@login_required
def profile_view(request):
    """Просмотр личного профиля."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    portfolio = profile.portfolio.all()
    my_services = ProviderService.objects.filter(user=request.user)
    reviews = Review.objects.filter(provider=request.user).order_by('-created_at')

    context = {
        'profile': profile,
        'portfolio': portfolio,
        'my_services': my_services,
        'reviews': reviews,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Редактирование профиля и портфолио."""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, _('Профиль обновлён.'))
            return redirect('profile')
        else:
            messages.error(request, _('Ошибка при сохранении профиля.'))
    else:
        form = ProfileEditForm(instance=profile)

    portfolio_form = PortfolioUploadForm()
    portfolio = profile.portfolio.all()

    return render(request, 'accounts/edit_profile.html', {
        'form': form,
        'portfolio_form': portfolio_form,
        'portfolio': portfolio,
    })


@login_required
def upload_portfolio(request):
    """Загрузка фото в портфолио."""
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PortfolioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save(commit=False)
            img.profile = profile
            img.save()
            messages.success(request, _('Фото добавлено в портфолио.'))
        else:
            messages.error(request, _('Не удалось загрузить фото.'))
    return redirect('edit_profile')


@login_required
def delete_portfolio(request, pk):
    """Удаление фото из портфолио."""
    img = get_object_or_404(PortfolioImage, pk=pk, profile__user=request.user)
    img.delete()
    messages.success(request, _('Фото удалено.'))
    return redirect('edit_profile')


def public_profile(request, username):
    """Публичный профиль исполнителя."""
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    services = ProviderService.objects.filter(user=user, is_active=True)
    reviews = Review.objects.filter(provider=user).order_by('-created_at')
    portfolio = profile.portfolio.all()

    return render(request, 'accounts/public_profile.html', {
        'profile_user': user,
        'profile': profile,
        'services': services,
        'reviews': reviews,
        'portfolio': portfolio,
    })