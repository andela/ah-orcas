from django.urls import path
from rest_framework_swagger.views import get_swagger_view

from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    ForgetPassword,
    ResetPassword)
from . import views

schema_view = get_swagger_view(title="Orcas API Documentation")

urlpatterns = [
    path(
        '',
        schema_view,
        name="main-view"),
    path(
        'user/<int:pk>',
        UserRetrieveUpdateAPIView.as_view()),
    path(
        'users/',
        RegistrationAPIView.as_view(),
        name='register'),
    path(
        'users/login/',
        LoginAPIView.as_view()),
    path(
        'users/verify/<str:token>',
        views.VerifyAPIView.as_view(),
        name='verify'),
    path(
        'users/forget/',
        ForgetPassword.as_view(),
        name='forget'),
    path(
        'users/reset/<str:hashed_email>/<str:token>',
        ResetPassword.as_view(),
        name='reset')]
