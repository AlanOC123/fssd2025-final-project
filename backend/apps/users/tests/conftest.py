import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker

from apps.users.constants import MembershipVocabulary
from apps.users.models import (
    MembershipStatus,
    TrainerClientMembership,
    TrainingGoal,
)

User = get_user_model()

pytestmark = pytest.mark.django_db


# ── Credentials ───────────────────────────────────────────────────────────────


@pytest.fixture
def test_emails():
    return {
        "base": "test@apex.com",
        "admin": "admin@apex.com",
        "client": "client@apex.com",
        "trainer": "trainer@apex.com",
        "add_trainer": "trainer2@apex.com",
    }


@pytest.fixture
def test_password():
    return "password123"


# ── Membership status fixtures ────────────────────────────────────────────────
# Rows seeded by root conftest seed_program_vocab — just fetch them.


@pytest.fixture
def active_status():
    obj, _ = MembershipStatus.objects.get_or_create(
        code=MembershipVocabulary.ACTIVE, defaults={"label": "Active"}
    )
    return obj


@pytest.fixture
def pending_status():
    obj, _ = MembershipStatus.objects.get_or_create(
        code=MembershipVocabulary.PENDING, defaults={"label": "Pending Trainer Review"}
    )
    return obj


@pytest.fixture
def rejected_status():
    obj, _ = MembershipStatus.objects.get_or_create(
        code=MembershipVocabulary.REJECTED, defaults={"label": "Rejected"}
    )
    return obj


@pytest.fixture
def dissolved_status():
    obj, _ = MembershipStatus.objects.get_or_create(
        code=MembershipVocabulary.DISSOLVED_BY_CLIENT,
        defaults={"label": "Dissolved by Client"},
    )
    return obj


@pytest.fixture
def dissolved_by_trainer_status():
    obj, _ = MembershipStatus.objects.get_or_create(
        code=MembershipVocabulary.DISSOLVED_BY_TRAINER,
        defaults={"label": "Dissolved by Trainer"},
    )
    return obj


# ── Anonymous users for service/model tests ───────────────────────────────────
# These shadow the root conftest trainer_user/client_user intentionally —
# service tests need users without fixed emails.


@pytest.fixture
def client_user():
    return baker.make(User, is_client=True)


@pytest.fixture
def trainer_user_a():
    return baker.make(User, is_trainer=True)


@pytest.fixture
def trainer_user_b():
    return baker.make(User, is_trainer=True)


# ── Training goals ────────────────────────────────────────────────────────────


@pytest.fixture
def goal_strength():
    obj, _ = TrainingGoal.objects.get_or_create(
        code="STRENGTH", defaults={"label": "Strength"}
    )
    return obj


@pytest.fixture
def goal_muscle_mass():
    obj, _ = TrainingGoal.objects.get_or_create(
        code="MUSCLE_MASS", defaults={"label": "Muscle Mass"}
    )
    return obj


# ── Profiles ──────────────────────────────────────────────────────────────────


@pytest.fixture
def client():
    return baker.make(User, is_client=True).client_profile


@pytest.fixture
def trainer_a():
    return baker.make(User, is_trainer=True).trainer_profile


@pytest.fixture
def trainer_b():
    return baker.make(User, is_trainer=True).trainer_profile


@pytest.fixture
def trainer_c():
    return baker.make(User, is_trainer=True).trainer_profile


@pytest.fixture
def trainer_d():
    return baker.make(User, is_trainer=True).trainer_profile


# ── Configured matching fixtures ──────────────────────────────────────────────


@pytest.fixture
def client_strength_beginner(client, goal_strength, level_beginner):
    client.goal = goal_strength
    client.level = level_beginner
    client.save()
    return client


@pytest.fixture
def trainer_a_strength_beginner(trainer_a, goal_strength, level_beginner):
    trainer_a.accepted_goals.add(goal_strength)
    trainer_a.accepted_levels.add(level_beginner)
    return trainer_a


@pytest.fixture
def trainer_b_muscle_mass_beginner(trainer_b, goal_muscle_mass, level_beginner):
    trainer_b.accepted_goals.add(goal_muscle_mass)
    trainer_b.accepted_levels.add(level_beginner)
    return trainer_b


@pytest.fixture
def trainer_c_strength_intermediate(trainer_c, goal_strength, intermediate_level):
    trainer_c.accepted_goals.add(goal_strength)
    trainer_c.accepted_levels.add(intermediate_level)
    return trainer_c


@pytest.fixture
def trainer_d_strength_beginner(trainer_d, goal_strength, level_beginner):
    trainer_d.accepted_goals.add(goal_strength)
    trainer_d.accepted_levels.add(level_beginner)
    return trainer_d


# ── Membership world response fixtures ───────────────────────────────────────


@pytest.fixture
def trainer_a_membership_response(api_client, membership_world):
    api_client.force_authenticate(user=membership_world["trainer_a"])
    response = api_client.get("/api/v1/users/trainer-client-memberships/")
    return response, membership_world


@pytest.fixture
def client_membership_response(api_client, membership_world):
    api_client.force_authenticate(user=membership_world["client"])
    response = api_client.get("/api/v1/users/trainer-client-memberships/")
    return response, membership_world


# ── response_items override ───────────────────────────────────────────────────
# Users tests expect response_items to return just the data list,
# not the (status_code, data) tuple that the root conftest returns.


@pytest.fixture
def response_items():
    def extract(response):
        data = response.data
        return data["results"] if isinstance(data, dict) and "results" in data else data

    return extract
