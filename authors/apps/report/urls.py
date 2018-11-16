from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from .views import (
    ArticleReportAPIView,
)

schema_view = get_swagger_view(title="Report")

urlpatterns = [
    path(
        'article/report/',
        ArticleReportAPIView.as_view(),
        name='rep'),
]
