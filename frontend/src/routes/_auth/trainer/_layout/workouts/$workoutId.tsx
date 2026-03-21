import { createFileRoute } from '@tanstack/react-router'
import { TrainerWorkoutDetail } from '@/features/workouts/components/TrainerWorkoutDetail'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/trainer/_layout/workouts/$workoutId')({
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),
    component: function TrainerWorkoutDetailRoute() {
        const { workoutId } = Route.useParams()
        return <TrainerWorkoutDetail workoutId={workoutId} />
    },
})
