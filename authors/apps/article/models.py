# this is how the db will be structured.
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework.reverse import reverse as api_reverse
from django.db import models
from django.utils.translation import pgettext_lazy as _

from authors.apps.authentication.models import User
from authors.apps.core.models import TimestampedModel

'''Django-autoslug is a reusable Django library
that provides an improved slug field which can automatically:
populate itself from another field and preserve
 uniqueness of the value'''
from autoslug import AutoSlugField
from versatileimagefield.fields import VersatileImageField


class Article(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        related_name='author',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    # creates a random identifier for a particular article from the title
    # field.
    slug = AutoSlugField(
        populate_from='title',
        blank=True,
        null=True,
        unique=True)
    title = models.CharField(
        _('Article field', 'title'),
        unique=True,
        max_length=128
    )
    description = models.TextField(
        _('Article Field', 'description'),
        blank=True,
        null=True
    )
    body = models.TextField(
        _('Article Field', 'body'),
        blank=True,
        null=True
    )
    image = VersatileImageField(
        'Image',
        upload_to='article/',
        width_field='width',
        height_field='height',
        blank=True,
        null=True
    )
    height = models.PositiveIntegerField(
        'Image Height',
        blank=True,
        null=True
    )
    width = models.PositiveIntegerField(
        'Image Width',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        _('Article field', 'created at'),
        auto_now_add=True,
        editable=False
    )
    updated_at = models.DateTimeField(
        _('Article field', 'updated at'),
        auto_now=True
    )

    tags = ArrayField(
        models.CharField(max_length=10, blank=True),
        blank=True,
        null=True
    )

    class Meta:
        app_label = "article"

    def __str__(self):
        return self.title

    def api_url(self, request=None):
        return api_reverse("article:detail",
                           kwargs={'slug': self.slug}, request=request)


class RateArticle(models.Model):
    """
    This is the article class. It holds data for the article.
    """
    rater = models.ForeignKey(
        "authentication.User",
        related_name="ratearticle",
        on_delete=models.CASCADE)  # link with the user who rated
    article = models.ForeignKey(
        "article.Article",
        related_name="ratearticle",
        on_delete=models.CASCADE)  # link with the article being rated
    rate = models.IntegerField(null=False, blank=False,
                               validators=[
                                   MaxValueValidator(5),
                                   MinValueValidator(1)
                               ])  # rate value column

    def __str__(self):
        """
        Return a human readable format
        """
        return self.rate


class LikeDislikeArticle(models.Model):
    """
    This model holds likes of an article in a boolean format.
    """
    liker = models.ForeignKey(
        "authentication.User",
        related_name="likearticle",
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        "article.Article",
        related_name="likearticle",
        on_delete=models.CASCADE)
    is_liked = models.BooleanField(
        default=False,
        null=False,
        blank=False
    )
    is_disliked = models.BooleanField(
        default=False,
        null=False,
        blank=False
    )

    def __str__(self):
        "return human readable format"
        return self.is_liked


class Comments(TimestampedModel):
    """
    This class handles the comments of a single article
    """
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=False,
        on_delete=models.CASCADE,
        related_name='thread')
    body = models.TextField(max_length=200)
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        blank=True,
        null=True)
    article = models.ForeignKey(
        Article,
        related_name='comments',
        on_delete=models.CASCADE,
        null=True)

    def __str__(self):
        return self.body
