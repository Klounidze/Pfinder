from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('dialog/<str:username>/', views.dialog, name='dialog'),
    path('start/<int:user_id>/', views.get_or_create_dialog, name='start_dialog'),

    # API
    path('api/send/', views.send_message_api, name='send_message_api'),
    path('api/messages/<str:username>/', views.get_messages_api, name='get_messages_api'),
    path('api/mark_all_read/', views.mark_all_read_api, name='mark_all_read_api'),
    path('api/notifications/count/', views.notifications_count_api, name='notifications_count_api'),
]