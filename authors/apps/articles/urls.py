from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from .views import Rate, ArticleRate

schema_view = get_swagger_view(title="Articles")

urlpatterns = [
    path(
        'article/<str:slug>/rate/',
        Rate.as_view(), name="rate"),
    path(
        'article/rate/<str:pk>/',
        ArticleRate.as_view(), name="view_rate"),
]
