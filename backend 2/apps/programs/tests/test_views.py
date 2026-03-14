import pytest
import pytest_django
from django.contrib.auth import get_user_model
from model_bakery import baker

from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.users.models import ClientProfile, TrainerClientMembership, TrainerProfile
