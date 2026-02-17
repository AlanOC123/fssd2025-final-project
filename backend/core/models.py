import uuid

from django.db import models


class ApexModel(models.Model):
    """
    Abstract User model that provides a base UUID instead of integer for the primary key
    It also adds a created at and updated at field automatically to reduce duplication
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
