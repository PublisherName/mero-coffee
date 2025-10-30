from django.db import models


class CreatorPost(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("members", "Members Only"),
    ]

    creator = models.ForeignKey(
        "creators.CreatorProfile", on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default="public")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
