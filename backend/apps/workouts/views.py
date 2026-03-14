from django.core.exceptions import ValidationError as DjangoValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.workouts.models import (
    Workout,
    WorkoutCompletionRecord,
    WorkoutExercise,
    WorkoutExerciseCompletionRecord,
    WorkoutSet,
    WorkoutSetCompletionRecord,
)
from apps.workouts.serializers import (
    CompleteSetSerializer,
    SkipSetSerializer,
    StartExerciseSerializer,
    StartWorkoutSerializer,
    WorkoutCompletionReadSerializer,
    WorkoutExerciseCompletionReadSerializer,
    WorkoutExerciseReadSerializer,
    WorkoutExerciseWriteSerializer,
    WorkoutListSerializer,
    WorkoutReadSerializer,
    WorkoutSetCompletionReadSerializer,
    WorkoutSetReadSerializer,
    WorkoutSetWriteSerializer,
    WorkoutWriteSerializer,
)
from apps.workouts.services.completions import WorkoutCompletionService

# Helpers


def _raise_drf_validation_error(exc):
    if hasattr(exc, "message_dict"):
        raise ValidationError(exc.message_dict)
    raise ValidationError(exc.messages)


# Prescriptive viewsets (trainer-authored content)


class WorkoutViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Trainer: full CRUD within a phase that is still live.
    Client: read-only, scoped to their own memberships.
    Phase-liveness guard lives in the service; this viewset
    handles routing and ownership scoping only.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["program_phase", "planned_date"]

    def get_queryset(self):
        user = self.request.user

        queryset = Workout.objects.select_related(
            "program_phase",
            "program_phase__status",
            "program_phase__program",
            "program_phase__program__trainer_client_membership",
            "program_phase__program__trainer_client_membership__trainer__user",
            "program_phase__program__trainer_client_membership__client__user",
        ).prefetch_related(
            "exercises",
            "exercises__exercise",
            "exercises__sets",
        )

        if user.is_trainer:
            return queryset.filter(
                program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        if user.is_client:
            return queryset.filter(
                program_phase__program__trainer_client_membership__client=user.client_profile
            )

        return queryset.none()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return WorkoutWriteSerializer
        if self.action == "list":
            return WorkoutListSerializer
        return WorkoutReadSerializer

    def _validate_trainer_owns_workout(self, workout):
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can modify workouts.")

        membership = workout.program_phase.program.trainer_client_membership
        if membership is None:
            raise PermissionDenied(
                "This workout is not attached to an active membership."
            )

        if membership.trainer.user != user:
            raise PermissionDenied("You can only modify workouts you created.")

    def create(self, request, *args, **kwargs):
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can create workouts.")

        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Ownership check against the phase being written to
        phase = input_serializer.validated_data["program_phase"]
        membership = phase.program.trainer_client_membership

        if membership is None or membership.trainer.user != request.user:
            raise PermissionDenied("You can only add workouts to your own programs.")

        try:
            workout = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutReadSerializer(
            workout, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        workout = self.get_object()
        self._validate_trainer_owns_workout(workout)

        input_serializer = self.get_serializer(
            workout, data=request.data, partial=kwargs.pop("partial", False)
        )
        input_serializer.is_valid(raise_exception=True)

        try:
            workout = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutReadSerializer(
            workout, context=self.get_serializer_context()
        )
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        workout = self.get_object()
        self._validate_trainer_owns_workout(workout)
        workout.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkoutExerciseViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workout"]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutExercise.objects.select_related(
            "workout",
            "workout__program_phase",
            "workout__program_phase__program__trainer_client_membership__trainer__user",
            "workout__program_phase__program__trainer_client_membership__client__user",
            "exercise",
        ).prefetch_related("sets")

        if user.is_trainer:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        if user.is_client:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__client=user.client_profile
            )

        return queryset.none()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return WorkoutExerciseWriteSerializer
        return WorkoutExerciseReadSerializer

    def _validate_trainer_owns_exercise(self, workout_exercise):
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can modify workout exercises.")

        membership = (
            workout_exercise.workout.program_phase.program.trainer_client_membership
        )
        if membership is None or membership.trainer.user != user:
            raise PermissionDenied(
                "You can only modify exercises for your own workouts."
            )

    def create(self, request, *args, **kwargs):
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can add exercises to a workout.")

        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        workout = input_serializer.validated_data["workout"]
        membership = workout.program_phase.program.trainer_client_membership

        if membership is None or membership.trainer.user != request.user:
            raise PermissionDenied("You can only add exercises to your own workouts.")

        try:
            workout_exercise = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutExerciseReadSerializer(
            workout_exercise, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        workout_exercise = self.get_object()
        self._validate_trainer_owns_exercise(workout_exercise)

        input_serializer = self.get_serializer(
            workout_exercise, data=request.data, partial=kwargs.pop("partial", False)
        )
        input_serializer.is_valid(raise_exception=True)

        try:
            workout_exercise = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutExerciseReadSerializer(
            workout_exercise, context=self.get_serializer_context()
        )
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        workout_exercise = self.get_object()
        self._validate_trainer_owns_exercise(workout_exercise)
        workout_exercise.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkoutSetViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workout_exercise"]

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutSet.objects.select_related(
            "workout_exercise",
            "workout_exercise__workout",
            "workout_exercise__workout__program_phase__program__trainer_client_membership__trainer__user",
            "workout_exercise__workout__program_phase__program__trainer_client_membership__client__user",
        )

        if user.is_trainer:
            return queryset.filter(
                workout_exercise__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        if user.is_client:
            return queryset.filter(
                workout_exercise__workout__program_phase__program__trainer_client_membership__client=user.client_profile
            )

        return queryset.none()

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return WorkoutSetWriteSerializer
        return WorkoutSetReadSerializer

    def _validate_trainer_owns_set(self, workout_set):
        user = self.request.user

        if not user.is_trainer:
            raise PermissionDenied("Only trainers can modify workout sets.")

        membership = (
            workout_set.workout_exercise.workout.program_phase.program.trainer_client_membership
        )
        if membership is None or membership.trainer.user != user:
            raise PermissionDenied("You can only modify sets for your own workouts.")

    def create(self, request, *args, **kwargs):
        if not request.user.is_trainer:
            raise PermissionDenied("Only trainers can add sets to an exercise.")

        input_serializer = self.get_serializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        workout_exercise = input_serializer.validated_data["workout_exercise"]
        membership = (
            workout_exercise.workout.program_phase.program.trainer_client_membership
        )

        if membership is None or membership.trainer.user != request.user:
            raise PermissionDenied("You can only add sets to your own workouts.")

        try:
            workout_set = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutSetReadSerializer(
            workout_set, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        workout_set = self.get_object()
        self._validate_trainer_owns_set(workout_set)

        input_serializer = self.get_serializer(
            workout_set, data=request.data, partial=kwargs.pop("partial", False)
        )
        input_serializer.is_valid(raise_exception=True)

        try:
            workout_set = input_serializer.save()
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutSetReadSerializer(
            workout_set, context=self.get_serializer_context()
        )
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        workout_set = self.get_object()
        self._validate_trainer_owns_set(workout_set)
        workout_set.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Completion viewsets (client-driven session recording)


class WorkoutSessionViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    The entry point for a client's workout session.
    All writes go through named actions backed by WorkoutCompletionService.
    No raw create/update/delete — the service owns the write contract.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["is_skipped", "workout__program_phase"]
    serializer_class = WorkoutCompletionReadSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutCompletionRecord.objects.select_related(
            "workout",
            "workout__program_phase",
            "workout__program_phase__status",
            "workout__program_phase__program__trainer_client_membership__client__user",
            "client",
        ).prefetch_related(
            "exercise_records",
            "exercise_records__workout_exercise",
            "exercise_records__workout_exercise__exercise",
            "exercise_records__set_records",
            "exercise_records__set_records__workout_set",
        )

        if user.is_client:
            return queryset.filter(client=user)

        if user.is_trainer:
            return queryset.filter(
                workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        return queryset.none()

    def _run_session_action(self, request, service_method, serializer_class=None):
        validated_data = {}
        if serializer_class is not None:
            input_serializer = serializer_class(data=request.data)
            input_serializer.is_valid(raise_exception=True)
            validated_data = input_serializer.validated_data

        try:
            result = service_method(
                client_user=request.user,
                **validated_data,
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutCompletionReadSerializer(
            result, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        return self._run_session_action(
            request=request,
            service_method=WorkoutCompletionService.start_workout,
            serializer_class=StartWorkoutSerializer,
        )

    @action(detail=False, methods=["post"], url_path="skip")
    def skip(self, request):
        return self._run_session_action(
            request=request,
            service_method=WorkoutCompletionService.skip_workout,
            serializer_class=StartWorkoutSerializer,
        )

    @action(detail=True, methods=["post"], url_path="finish")
    def finish(self, request, pk=None):
        session = self.get_object()

        try:
            session = WorkoutCompletionService.finish_workout(
                session=session,
                client_user=request.user,
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutCompletionReadSerializer(
            session, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class WorkoutExerciseRecordViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    Records a client starting or skipping an exercise within a session.
    No raw create — use the start and skip actions.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workout_completion_record", "is_skipped"]
    serializer_class = WorkoutExerciseCompletionReadSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutExerciseCompletionRecord.objects.select_related(
            "workout_completion_record",
            "workout_completion_record__client",
            "workout_exercise",
            "workout_exercise__exercise",
        ).prefetch_related(
            "set_records",
            "set_records__workout_set",
        )

        if user.is_client:
            return queryset.filter(workout_completion_record__client=user)

        if user.is_trainer:
            return queryset.filter(
                workout_completion_record__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        return queryset.none()

    def _run_exercise_action(self, request, service_method):
        input_serializer = StartExerciseSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        try:
            record = service_method(
                workout_exercise=input_serializer.validated_data["workout_exercise"],
                session=input_serializer.validated_data["session"],
                client_user=request.user,
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutExerciseCompletionReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="start")
    def start(self, request):
        return self._run_exercise_action(
            request=request,
            service_method=WorkoutCompletionService.start_exercise,
        )

    @action(detail=False, methods=["post"], url_path="skip")
    def skip(self, request):
        return self._run_exercise_action(
            request=request,
            service_method=WorkoutCompletionService.skip_exercise,
        )


class WorkoutSetRecordViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """
    The atomic write unit of the completion side.
    Clients complete or skip individual sets in real time.
    """

    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["exercise_completion_record", "is_skipped"]
    serializer_class = WorkoutSetCompletionReadSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = WorkoutSetCompletionRecord.objects.select_related(
            "exercise_completion_record",
            "exercise_completion_record__workout_completion_record__client",
            "workout_set",
            "workout_set__workout_exercise",
        )

        if user.is_client:
            return queryset.filter(
                exercise_completion_record__workout_completion_record__client=user
            )

        if user.is_trainer:
            return queryset.filter(
                exercise_completion_record__workout_completion_record__workout__program_phase__program__trainer_client_membership__trainer=user.trainer_profile
            )

        return queryset.none()

    @action(detail=False, methods=["post"], url_path="complete")
    def complete(self, request):
        input_serializer = CompleteSetSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            record = WorkoutCompletionService.complete_set(
                workout_set=data["workout_set"],
                exercise_record=data["exercise_record"],
                client_user=request.user,
                reps_completed=data["reps_completed"],
                weight_completed=data["weight_completed"],
                difficulty_rating=data.get("difficulty_rating"),
                reps_in_reserve=data.get("reps_in_reserve"),
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutSetCompletionReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="skip")
    def skip(self, request):
        input_serializer = SkipSetSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        try:
            record = WorkoutCompletionService.skip_set(
                workout_set=data["workout_set"],
                exercise_record=data["exercise_record"],
                client_user=request.user,
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = WorkoutSetCompletionReadSerializer(
            record, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
