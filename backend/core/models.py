import uuid

from django.db import models


class ApexModel(models.Model):
    """
    Abstract model that provides a base UUID instead of integer for the primary key
    It also adds a created at and updated at field automatically to reduce duplication
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class NormalisedLookupModel(ApexModel):
    """
    Core model the normalised tables build upon
    """

    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=50)
    order_index = models.SmallIntegerField(default=0)
    description = models.TextField(max_length=300, blank=True)

    class Meta:
        abstract = True
        ordering = ["order_index", "label"]

    def __str__(self) -> str:
        return self.label
