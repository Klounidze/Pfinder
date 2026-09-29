from django.contrib import admin
from .models import Profile, PortfolioImage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'service_type', 'country', 'city', 'is_provider')
    list_filter = ('service_type', 'is_provider', 'country')
    search_fields = ('user__username', 'phone', 'city')


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'caption', 'uploaded_at')
    list_filter = ('uploaded_at',)