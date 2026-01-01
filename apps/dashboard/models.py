from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


# TODO: Move this to apps.creators.models when needed
class CreatorPost(models.Model):
    class Visibility(TextChoices):
        PUBLIC = "public", _("Public")
        MEMBERS = "members", _("Members Only")

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    visibility = models.CharField(
        max_length=20, choices=Visibility.choices, default=Visibility.PUBLIC
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
