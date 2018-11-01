from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)
from . import views

urlpatterns = [
    path('user/<int:pk>', UserRetrieveUpdateAPIView.as_view()),
    path('users/', RegistrationAPIView.as_view(), name='register'),
    path('users/login/', LoginAPIView.as_view()),
    path('users/verify/<str:token>',
         views.VerifyAPIView.as_view(), name='verify'),
]
