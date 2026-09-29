from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import Profile, PortfolioImage


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True, label=_('Email'),
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'})
    )
    first_name = forms.CharField(
        required=False, label=_('Имя'),
        widget=forms.TextInput(attrs={'placeholder': _('Иван')})
    )
    last_name = forms.CharField(
        required=False, label=_('Фамилия'),
        widget=forms.TextInput(attrs={'placeholder': _('Иванов')})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Этот email уже зарегистрирован.'))
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': _('Логин'),
            'password1': _('Пароль'),
            'password2': _('Повторите пароль'),
        }
        for name, field in self.fields.items():
            field.widget.attrs.setdefault('class', 'form-control')
            if name in placeholders:
                field.widget.attrs.setdefault('placeholder', placeholders[name])


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class ProfileEditForm(forms.ModelForm):
    """Редактирование профиля + User полей."""

    first_name = forms.CharField(
        required=False, label=_('Имя'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        required=False, label=_('Фамилия'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False, label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ['phone', 'service_type', 'country', 'city', 'bio', 'avatar', 'is_provider']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 999 123-45-67'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Россия')}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Москва')}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                          'placeholder': _('Расскажите о себе и своих услугах...')}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_provider': forms.CheckboxInput(attrs={'class': 'form-check'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()
            profile.save()
        return profile


class PortfolioUploadForm(forms.ModelForm):
    class Meta:
        model = PortfolioImage
        fields = ['image', 'caption']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control',
                                               'placeholder': _('Описание работы')}),
        }