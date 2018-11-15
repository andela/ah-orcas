from django.db import models


class NotificationsFollower(models.Model):
    """
    This is class holds notification data for
    the user followers
    """
    follower = models.ForeignKey(
        "profiles.UserProfile",
        related_name='author_relation',
        on_delete=models.CASCADE)  # a user being followed

    followee = models.ForeignKey(
        "profiles.UserProfile",
        related_name='follower_relation',
        on_delete=models.CASCADE)  # a user following the follower

    article = models.ForeignKey(
        "article.Article",
        related_name='Article',
        on_delete=models.CASCADE)  # article created

    is_read = models.BooleanField(
        default=False,
        null=False,
        blank=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False)


class NotificationsArticle(models.Model):
    """
    This model holds notification data
    for users who have favourited
    an article
    """
    subscriber = models.ForeignKey(
        "authentication.User",
        related_name="notification_Favorite",
        on_delete=models.CASCADE)  # user who have favorited the article

    article = models.ForeignKey(
        "article.Article",
        related_name="notification_article",
        on_delete=models.CASCADE)

    is_read = models.BooleanField(
        default=False,
        null=False,
        blank=False)

    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False)
