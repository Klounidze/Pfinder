from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ProviderService, Review, Category


class ProviderServiceForm(forms.ModelForm):
    class Meta:
        model = ProviderService
        fields = ['category', 'title', 'description', 'price', 'price_unit',
                  'country', 'city', 'phone']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': _('Например: Няня для ребёнка 3-5 лет')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5,
                                                  'placeholder': _('Опишите услугу подробно...')}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1500'}),
            'price_unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('час')}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Россия')}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Москва')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 999 123-45-67'}),
        }


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f'{i} ★') for i in range(1, 6)],
        widget=forms.RadioSelect,
        label=_('Оценка')
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': _('Расскажите о своём опыте...')
            }),
        }