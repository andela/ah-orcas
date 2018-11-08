from django.db import models


class TimestampedModel(models.Model):
    """
    This class abstracts the models for timestamps
    The timestamps will be inherited in user model and profile model
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        # default ordering for models
        ordering = ['-created_at', '-updated_at']
