from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from .views import (
    ArticleCreateAPIView,
    ArticleListAPIView,
    ArticleDeleteAPIView,
    ArticleDetailAPIView,
    ArticleUpdateAPIView,
    Rate,
    ArticleRate
)

schema_view = get_swagger_view(title="Articles")

urlpatterns = [
    path(
        'article/',
        ArticleListAPIView.as_view(),
        name='list'),
    path(
        'article/create',
        ArticleCreateAPIView.as_view(),
        name='create'),
    path(
        'article/delete/<slug>/',
        ArticleDeleteAPIView.as_view(),
        name='delete'),
    path(
        'article/detail/<slug>/',
        ArticleDetailAPIView.as_view(),
        name='detail'),
    path(
        'article/update/<slug>/',
        ArticleUpdateAPIView.as_view(),
        name='update'),
    path(
        'article/<str:slug>/rate/',
        Rate.as_view(),
        name="rate"),
    path(
        'article/rate/<str:pk>/',
        ArticleRate.as_view(),
        name="view_rate"),
]
