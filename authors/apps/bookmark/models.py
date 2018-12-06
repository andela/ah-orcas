from django.db import models
from authors.apps.authentication.models import User
from authors.apps.article.models import Article


class Bookmark(models.Model):
    """Bookmark model"""
    article = models.ForeignKey(
        Article,
        related_name="bookmarked",
        null=True,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name="bookmarks",
        null=True,
        on_delete=models.CASCADE)
