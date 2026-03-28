from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.programs.constants import ProgramPhaseStatusesVocabulary
from apps.programs.models import Program, ProgramPhase, ProgramPhaseOption
from apps.programs.serializers import (
    ProgramAbandonSerializer,
    ProgramCompleteSerializer,
    ProgramDetailSerializer,
    ProgramListSerializer,
    ProgramPhaseListSerializer,
    ProgramPhaseOptionSerializer,
    ProgramPhaseReadSerializer,
    ProgramPhaseReasonSerializer,
    ProgramPhaseWriteSerializer,
    ProgramReviewSerializer,
    ProgramWriteSerializer,
)
from apps.programs.services.program_phases import ProgramPhaseService
from apps.programs.services.programs import ProgramService
from core.views import NormalisedLookupViewSet

from .filters import ProgramFilter


class ProgramPhaseOptionViewSet(NormalisedLookupViewSet):
    """ViewSet for managing ProgramPhaseOption lookup data."""

    serializer_class = ProgramPhaseOptionSerializer
    queryset = ProgramPhaseOption.objects.all()


class ProgramPhaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for managing ProgramPhase instances.

    Handles standard CRUD operations and custom lifecycle actions for program phases,
    enforcing role-based access control for trainers and clients.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["program", "status", "phase_option", "sequence_order"]

    def get_queryset(self):
        """Filters phases based on the user's role and associated membership.

        Returns:
            A queryset of ProgramPhase objects filtered by ownership.
        """
        user = self.request.user

        queryset = ProgramPhase.objects.select_related(
            "program",
            "program__status",
            "program__trainer_client_membership",
            "program__trainer_client_membership__trainer__user",
            "program__trainer_client_membership__client__user",
            "phase_option",
            "status",
            "created_by_trainer",
            "last_edited_by",
        )

        if user.is_trainer:
            return queryset.filter(
                program__trainer_client_membership__trainer=user.trainer_profile
            )

        if user.is_client:
            return queryset.filter(
                program__trainer_client_membership__client=user.client_profile
            )

        return queryset.none()

    def get_serializer_class(self):
        """Maps specific actions to their respective serializer classes.

        Returns:
            The serializer class appropriate for the current action.
        """
        if self.action == "create":
            return ProgramPhaseWriteSerializer

        if self.action == "list":
            return ProgramPhaseListSerializer

        if self.action == "skip":
            return ProgramPhaseReasonSerializer

        return ProgramPhaseReadSerializer

    def _raise_drf_validation_error(self, exc):
        """Converts Django ValidationErrors into DRF ValidationErrors.

        Args:
            exc: The caught Django ValidationError instance.

        Raises:
            ValidationError: A DRF-compatible validation error.
        """
        if hasattr(exc, "message_dict"):
            raise ValidationError(exc.message_dict)
        raise ValidationError(exc.messages)

    def _validate_trainer_can_manage_program(self, program):
        """Enforces permission rules for trainers managing program phases.

        Args:
            program: The Program instance to validate against.

        Raises:
            PermissionDenied: If the user is not a trainer, the program is
                detached, or the trainer does not own the membership.
        """
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can manage program phases.")

        membership = program.trainer_client_membership
        if membership is None:
            raise PermissionDenied("Cannot manage phases for a detached program.")

        if membership.trainer.user != user:
            raise PermissionDenied("You can only manage phases for programs you own.")

        if not membership.is_active:
            raise PermissionDenied("You can only manage phases for active memberships.")

    def create(self, request, *args, **kwargs):
        """Handles the creation of a new ProgramPhase via ProgramPhaseService.

        Returns:
            A Response object containing the serialized created phase.
        """
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        program = input_serializer.validated_data["program"]
        self._validate_trainer_can_manage_program(program)

        try:
            ProgramPhaseService._validate_program_allows_phase_mutation(program)

            phase = input_serializer.save(
                status=ProgramPhaseService._get_status(
                    ProgramPhaseStatusesVocabulary.PLANNED
                ),
                created_by_trainer=request.user,
                last_edited_by=request.user,
            )

            ProgramPhaseService._sync_next_phase(program)
            phase.refresh_from_db()

        except DjangoValidationError as exc:
            self._raise_drf_validation_error(exc)

        output_serializer = ProgramPhaseReadSerializer(
            phase, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def _run_phase_action(self, request, service_action, serializer_class=None):
        """Helper to execute phase-level service actions with validation.

        Args:
            request: The current request object.
            service_action: The service method to execute.
            serializer_class: Optional serializer for input validation.

        Returns:
            A Response object with updated phase data.
        """
        phase = self.get_object()
        self._validate_trainer_can_manage_program(phase.program)

        validated_data = {}
        if serializer_class is not None:
            input_serializer = serializer_class(data=request.data)
            input_serializer.is_valid(raise_exception=True)
            validated_data = input_serializer.validated_data

        try:
            phase = service_action(
                phase=phase,
                edited_by=request.user,
                **validated_data,
            )
        except DjangoValidationError as exc:
            self._raise_drf_validation_error(exc)

        output_serializer = ProgramPhaseReadSerializer(
            phase, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="mark-next")
    def mark_next(self, request, pk=None):
        """Transitions a phase to the 'NEXT' status."""
        return self._run_phase_action(
            request=request,
            service_action=ProgramPhaseService.mark_as_next,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Transitions a phase to the 'ACTIVE' status."""
        return self._run_phase_action(
            request=request,
            service_action=ProgramPhaseService.activate_phase,
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Transitions a phase to the 'COMPLETED' status."""
        return self._run_phase_action(
            request=request,
            service_action=ProgramPhaseService.complete_phase,
        )

    @action(detail=True, methods=["post"])
    def skip(self, request, pk=None):
        """Transitions a phase to the 'SKIPPED' status with a reason."""
        return self._run_phase_action(
            request=request,
            service_action=ProgramPhaseService.skip_phase,
            serializer_class=ProgramPhaseReasonSerializer,
        )

    @action(detail=True, methods=["post"], url_path="restore")
    def restore_to_planned(self, request, pk=None):
        """Restores a phase back to the 'PLANNED' status."""
        return self._run_phase_action(
            request=request,
            service_action=ProgramPhaseService.restore_to_planned,
        )


class ProgramViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    """ViewSet for managing training Program instances.

    Supports the program lifecycle including creation, review, and execution tracking.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProgramFilter

    def get_queryset(self):
        """Filters programs based on whether the user is a trainer or a client."""
        user = self.request.user

        queryset = Program.objects.select_related(
            "trainer_client_membership",
            "trainer_client_membership__trainer__user",
            "trainer_client_membership__client__user",
            "training_goal",
            "experience_level",
            "status",
            "created_by_trainer",
            "last_edited_by",
        ).prefetch_related(
            "phases",
            "phases__phase_option",
            "phases__status",
        )

        if user.is_trainer:
            return queryset.filter(
                trainer_client_membership__trainer=user.trainer_profile
            )

        if user.is_client:
            return queryset.filter(
                trainer_client_membership__client=user.client_profile
            )

        return queryset.none()

    def get_serializer_class(self):
        """Returns the serializer class based on the current action."""
        if self.action == "create":
            return ProgramWriteSerializer

        if self.action == "list":
            return ProgramListSerializer

        if self.action == "review":
            return ProgramReviewSerializer

        if self.action == "complete":
            return ProgramCompleteSerializer

        if self.action == "abandon":
            return ProgramAbandonSerializer

        return ProgramDetailSerializer

    def _raise_drf_validation_error(self, exc):
        """Common error mapping from Django to DRF."""
        if hasattr(exc, "message_dict"):
            raise ValidationError(exc.message_dict)
        raise ValidationError(exc.messages)

    def _validate_trainer_can_manage_membership(self, membership):
        """Validates that a trainer has administrative rights over a membership."""
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can perform this action.")

        if membership is None:
            raise PermissionDenied("Program is not attached to a membership.")

        if membership.trainer.user != user:
            raise PermissionDenied(
                "You can only manage programs for memberships you own."
            )

        if not membership.is_active:
            raise PermissionDenied(
                "You can only manage programs for active memberships."
            )

    def _validate_program_access_for_action(self, program):
        """Verifies if the requesting user has permission to act on a program.

        Args:
            program: The Program instance to check.

        Raises:
            PermissionDenied: If the user does not belong to the program's membership.
        """
        user = self.request.user
        membership = program.trainer_client_membership

        if membership is None:
            raise PermissionDenied("Program is not attached to a membership.")

        if user.is_trainer:
            if membership.trainer.user != user:
                raise PermissionDenied(
                    "You can only manage programs for memberships you own."
                )
            return

        if user.is_client:
            if membership.client.user != user:
                raise PermissionDenied("You can only act on your own programs.")
            return

        raise PermissionDenied("You do not have access to this program.")

    def create(self, request, *args, **kwargs):
        """Creates a new training program for a client membership."""
        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        membership = input_serializer.validated_data["trainer_client_membership"]
        self._validate_trainer_can_manage_membership(membership)

        try:
            program = ProgramService.create(
                trainer_user=request.user,
                trainer_client_membership=membership,
                program_name=input_serializer.validated_data["program_name"],
                training_goal=input_serializer.validated_data["training_goal"],
                experience_level=input_serializer.validated_data["experience_level"],
            )
        except DjangoValidationError as exc:
            self._raise_drf_validation_error(exc)

        output_serializer = ProgramDetailSerializer(
            program, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def _run_program_action(self, request, service_action, serializer_class=None):
        """Generic runner for program-level lifecycle actions."""
        program = self.get_object()
        self._validate_program_access_for_action(program)

        validated_data = {}
        if serializer_class is not None:
            input_serializer = serializer_class(data=request.data)
            input_serializer.is_valid(raise_exception=True)
            validated_data = input_serializer.validated_data

        try:
            program = service_action(
                program=program,
                **validated_data,
            )
        except DjangoValidationError as exc:
            self._raise_drf_validation_error(exc)

        output_serializer = ProgramDetailSerializer(
            program, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="submit-for-review")
    def submit_for_review(self, request, pk=None):
        """Submits the program for client review."""
        return self._run_program_action(
            request=request,
            service_action=lambda **kwargs: ProgramService.submit_for_review(
                program=kwargs["program"],
                submitting_user=request.user,
            ),
        )

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        """Records a client's review decision for the program."""
        return self._run_program_action(
            request=request,
            service_action=lambda **kwargs: ProgramService.reviewed_by_client(
                program=kwargs["program"],
                reviewed_by_user=request.user,
                feedback_notes=kwargs.get("feedback_notes", ""),
                is_accepted=kwargs["is_accepted"],
            ),
            serializer_class=ProgramReviewSerializer,
        )

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Transitions the program to the 'IN_PROGRESS' state."""
        return self._run_program_action(
            request=request,
            service_action=lambda **kwargs: ProgramService.start_program(
                program=kwargs["program"],
                started_by_user=request.user,
            ),
        )

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Marks the program as successfully completed."""
        return self._run_program_action(
            request=request,
            service_action=lambda **kwargs: ProgramService.complete_program(
                program=kwargs["program"],
                completed_by_user=request.user,
                completion_notes=kwargs["completion_notes"],
            ),
            serializer_class=ProgramCompleteSerializer,
        )

    @action(detail=True, methods=["post"])
    def abandon(self, request, pk=None):
        """Records the premature abandonment of a program."""
        return self._run_program_action(
            request=request,
            service_action=lambda **kwargs: ProgramService.abandon_program(
                program=kwargs["program"],
                abandoned_by_user=request.user,
                abandonment_reason=kwargs["abandonment_reason"],
            ),
            serializer_class=ProgramAbandonSerializer,
        )
