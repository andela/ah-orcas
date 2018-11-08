from django.urls import path

from authors.apps.profiles.views import ProfileListAPIView
from .views import ProfileRetrieveAPIView

profiles = 'profiles/'

urlpatterns = [
    path(profiles, ProfileListAPIView.as_view(), name='all_profiles'),
    path(
        'profiles/<username>/',
        ProfileRetrieveAPIView.as_view(),
        name='profile'),
]
