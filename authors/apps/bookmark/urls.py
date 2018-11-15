from django.urls import path
from rest_framework_swagger.views import get_swagger_view
from .views import (
    BookmarkAPIView
)

schema_view = get_swagger_view(title="Bookmarks")

urlpatterns = [

    path('articles/bookmark/<slug>/',
         BookmarkAPIView.as_view(),
         name="bookmark"),
]
