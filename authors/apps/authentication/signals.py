from django.db.models.signals import post_save
from django.dispatch import receiver

from authors.apps.profiles.models import UserProfile
from .models import User


@receiver(post_save, sender=User)
def create_related_profile(instance, created, *args, **kwargs):
    """
    checks if the save causing the received signal
    is the one that creates a user instance
    If the save that caused the signal is an update then,
    a user already exists in the database
    """
    if instance and created:
        instance.profile = UserProfile.objects.create(user=instance)
