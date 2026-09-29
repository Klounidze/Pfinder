from django.contrib import admin
from .models import Category, ProviderService, Order, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name_ru', 'name_en', 'icon')


@admin.register(ProviderService)
class ProviderServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'city', 'country', 'price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'country')
    search_fields = ('title', 'description', 'city')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'service', 'client', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'provider', 'service', 'rating', 'created_at')
    list_filter = ('rating',)