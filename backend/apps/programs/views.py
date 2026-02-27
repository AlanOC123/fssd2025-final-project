from rest_framework import permissions, viewsets

from apps.programs.models import Program
from apps.programs.serializers import ProgramSerializer


class ProgramViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProgramSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_trainer:
            return Program.objects.none()

        return (
            Program.objects.filter(
                trainer_client_membership__client=user.client_profile
            )
            .select_related("trainer_goal", "experience_level")
            .prefetch_related("phases__phase_option")
        )
