from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class Article(models.Model):
    """
    This is the RateArticle class. It holds data for rating an article.
    """

    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    body = models.TextField()
    author = models.ForeignKey('authentication.User',
                               related_name='articles',
                               on_delete=models.CASCADE)

    def __str__(self):
        """
        Return article with human readable format
        """
        return self.title


class RateArticle(models.Model):
    """
    This is the article class. It holds data for the article.
    """
    rater = models.ForeignKey(
        "authentication.User",
        related_name="ratearticle",
        on_delete=models.CASCADE)  # link with the user who rated
    article = models.ForeignKey(
        "articles.Article",
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
