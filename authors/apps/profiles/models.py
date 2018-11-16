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

    # many to many relationship, meaning both sides of the
    # profile can have more than one follower
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )

    class Meta:
        app_label = "profiles"

    def __str__(self):
        return self.user.username

    def follow(self, my_profile):
        """
        follow my profile if you are not following me yet
        :param my_profile: profile to follow
        :return: none
        """
        self.follows.add(my_profile)

    def unfollow(self, my_profile):
        """
        quit following me if you are are already following me
        :param my_profile: profile to unfollow
        :return: none
        """
        self.follows.remove(my_profile)

    def is_following(self, profile):
        """
        check if am following the other profile
        :param profile: the other profile
        :return: True if am following the other profile else False
        """
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, my_profile):
        """check if the the other profile is following my profile"""
        return self.followed_by.filter(pk=my_profile.pk).exists()
