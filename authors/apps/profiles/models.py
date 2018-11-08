from django.db import models
from authors.apps.core.models import TimestampedModel


class UserProfile(TimestampedModel):
    """
    This class ensures that there is only one to one relationship
    between the Profile and User models
    """
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )
    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)

    def __str__(self):
        return self.user.username
