import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from apps.users.models import MembershipStatus, TrainerClientMembership

User = get_user_model()


@pytest.fixture
def api_client():
    """Make an API Client available for use throughout testing"""
    return APIClient()


@pytest.mark.django_db
class TestMembershipLifecycleAPI:
    """Verifies integrity of client trainer memberships"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        # Status
        self.status_pending = baker.make(
            MembershipStatus, status_name="PENDING_TRAINER_REVIEW"
        )
        self.status_active = baker.make(MembershipStatus, status_name="ACTIVE")
        self.status_rejected = baker.make(MembershipStatus, status_name="REJECTED")
        self.status_archived = baker.make(
            MembershipStatus, status_name="CLIENT_DISSOLVED"
        )

        # Actors
        self.client = baker.make(User, is_client=True)
        self.trainer = baker.make(User, is_trainer=True)
        self.trainer_b = baker.make(User, is_trainer=True)

    def test_client_can_create_pending_request(self, api_client):
        """Test POST /trainer-client-membership/"""

        # Authenticate as client
        api_client.force_authenticate(user=self.client)

        # Make a request to the trainer
        payload = {"trainer_id": self.trainer.trainer_profile.id}
        response = api_client.post("/api/v1/users/trainer-client-memberships/", payload)

        # Assertions
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status_name"] == self.status_pending.status_name
        assert response.data["trainer_id"] == self.trainer.trainer_profile.id

    def test_trainer_cannot_create_request(self, api_client):
        """Tests trainer cannot post a request to spam a client"""

        # Authenticate as the trainer
        api_client.force_authenticate(user=self.trainer)

        # Try make a request
        payload = {"trainer_id": self.trainer.trainer_profile.id}
        response = api_client.post("/api/v1/users/trainer-client-memberships/", payload)

        # Should trigger Permission denied
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_client_anti_spam_validation(self, api_client):
        """Tests a client cannot spam trainers with requests"""
        # Make an existing membership
        baker.make(
            TrainerClientMembership,
            client=self.client.client_profile,
            status=self.status_pending,
        )

        # Try create another one
        api_client.force_authenticate(user=self.client)
        payload = {"trainer_id": self.trainer.trainer_profile.id}
        response = api_client.post("/api/v1/users/trainer-client-memberships/", payload)

        # Should fail
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "You already have an active or pending trainer request." in str(
            response.data
        )

    def test_trainer_can_accept_pending_request(self, api_client):
        """Tests trainers can accept a pending request only"""
        membership = baker.make(
            TrainerClientMembership,
            client=self.client.client_profile,
            trainer=self.trainer.trainer_profile,
            status=self.status_pending,
        )

        api_client.force_authenticate(user=self.trainer)
        payload = {"status_id": self.status_active.id}
        response = api_client.patch(
            f"/api/v1/users/trainer-client-memberships/{membership.id}/", payload
        )

        assert response.status_code == status.HTTP_200_OK

        membership.refresh_from_db()

        assert membership.status == self.status_active
        assert membership.is_active is True

    def test_trainer_cannot_hijack_other_client(self, api_client):
        """Tests memberships no related to trainers cannot be found"""
        membership = baker.make(
            TrainerClientMembership,
            client=self.client.client_profile,
            trainer=self.trainer.trainer_profile,
            status=self.status_pending,
        )

        api_client.force_authenticate(user=self.trainer_b)
        payload = {"status_id": self.status_active.id}
        response = api_client.patch(
            f"/api/v1/users/trainer-client-memberships/{membership.id}/", payload
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_client_can_dissolve_membership_and_create_a_new_one(self, api_client):
        """Tests if clients can dissolve a membership and create a new one"""

        # Create an active membership
        membership = baker.make(
            TrainerClientMembership,
            client=self.client.client_profile,
            trainer=self.trainer.trainer_profile,
            status=self.status_active,
        )

        # Client dissolves it
        api_client.force_authenticate(user=self.client)
        payload = {"status_id": self.status_archived.id}
        response = api_client.patch(
            f"/api/v1/users/trainer-client-memberships/{membership.id}/", payload
        )

        assert response.status_code == status.HTTP_200_OK

        # Get fresh from memory
        membership.refresh_from_db()

        assert membership.status == self.status_archived
        assert membership.is_active is False

        # Client (still authenticated) posts a new request
        new_mem_payload = {"trainer_id": self.trainer_b.trainer_profile.id}
        new_response = api_client.post(
            "/api/v1/users/trainer-client-memberships/", new_mem_payload
        )

        assert new_response.status_code == status.HTTP_201_CREATED
        assert new_response.data["status_name"] == self.status_pending.status_name
        assert new_response.data["trainer_id"] == self.trainer_b.trainer_profile.id

        new_mem_id = new_response.data["id"]

        print(new_mem_id)

        # Trainer B accepts request
        api_client.force_authenticate(user=self.trainer_b)
        new_mem_update_payload = {"status_id": self.status_active.id}
        new_response_update = api_client.patch(
            f"/api/v1/users/trainer-client-memberships/{new_mem_id}/",
            new_mem_update_payload,
        )

        assert new_response_update.status_code == status.HTTP_200_OK

        # Assert status of new request
        new_mem = TrainerClientMembership.objects.get(
            trainer=self.trainer_b.trainer_profile
        )
        assert new_mem.status == self.status_active
        assert new_mem.is_active is True
