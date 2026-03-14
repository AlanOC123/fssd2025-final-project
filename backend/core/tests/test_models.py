import uuid

import pytest
from django.db import models
from django.test import TestCase
from model_bakery import baker

from core.models import ApexModel, NormalisedLookupModel


class DummyModel(ApexModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "core"


class TestApexModel(TestCase):
    def test_apex_model_fields(self):
        """
        Test that models inheriting from ApexModel automatically get:
        - A UUID primary key
        - A created_at timestamp
        - An updated_at timestamp
        """

        # Instance
        obj = DummyModel.objects.create(name="Test Item")

        # ASSERTIONS

        # ID should be a UUID instance
        self.assertIsInstance(obj.id, uuid.UUID)

        # Timestamps should be populated
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)

        # Updated at should change on save
        original_time = obj.updated_at
        obj.name = "Updated Name"
        obj.save()

        self.assertNotEqual(obj.updated_at, original_time)


class DummyLookupModel(NormalisedLookupModel):
    class Meta:
        app_label = "core"


@pytest.mark.django_db
class TestNormalisationModel:
    def test_normalised_table_fields(self):
        """Tests a normalised table is created with a code and a display name"""

        obj = baker.make(
            DummyLookupModel,
            code="ACTIVE",
            label="Active",
            order_index=1,
            description="Test Description",
        )

        assert obj.code == "ACTIVE"
        assert obj.label == "Active"
        assert obj.order_index == 1
        assert obj.description == "Test Description"
        assert str(obj) == "Active"
