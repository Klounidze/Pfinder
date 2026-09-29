from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add_service, name='add_provider'),
    path('service/<int:pk>/', views.service_detail, name='service_detail'),
    path('service/<int:pk>/order/', views.create_order, name='create_order'),
    path('orders/', views.my_orders, name='my_orders'),
    path('search/', views.search_results, name='search_results'),
]