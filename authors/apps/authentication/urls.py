from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from . import views
from .views import (
    ForgetPassword,
    ResetPassword,
    LoginAPIView, RegistrationAPIView, UserUpdateAPIView,
    SocialAuthView)

schema_view = get_swagger_view(title="Orcas API Documentation")

urlpatterns = [
    path(
        '',
        schema_view,
        name="main-view"),
    path(
        'users/',
        RegistrationAPIView.as_view(),
        name='register'),
    path(
        'users/login/',
        LoginAPIView.as_view(), name="login"),
    path(
        'user/',
        UserUpdateAPIView.as_view(),
        name='update_profile'),
    path(
        'users/login/',
        LoginAPIView.as_view(), name='login'),
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
        name='reset'),
    path('social_auth/', SocialAuthView.as_view(), name="social_auth")]
