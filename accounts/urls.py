from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/portfolio/upload/', views.upload_portfolio, name='upload_portfolio'),
    path('profile/portfolio/delete/<int:pk>/', views.delete_portfolio, name='delete_portfolio'),
    path('u/<str:username>/', views.public_profile, name='public_profile'),
]