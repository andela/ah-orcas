from django.urls import path
from .views import Notification


urlpatterns = [
    path(
        'notifications/<str:pk>/<str:follower>',
        Notification.as_view(),
        name='notifications_post'),
    path("notifications",
         Notification.as_view(),
         name="notifications_get"), ]
