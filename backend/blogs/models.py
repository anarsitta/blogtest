from django.db import models
from django.conf import settings

class Blog(models.Model):
    title = models.CharField(
        max_length=255
    )
    description = models.TextField()
    is_private = models.BooleanField(
        default=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs'
    )

    def __str__(self):
        return self.title
