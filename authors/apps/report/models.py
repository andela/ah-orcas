from django.db import models
from django.utils.translation import pgettext_lazy as _
from django.contrib.auth import get_user_model


class Report(models.Model):
    """
    Store reported articles for Admin to review
    """
    reporter = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    title = models.TextField(
        _('Report field', 'title'),
        blank=True,
        null=True
    )
    body = models.TextField(
        _('Report Field', 'body'),
        blank=True,
        null=True
    )

    class Meta:
        app_label = "report"
