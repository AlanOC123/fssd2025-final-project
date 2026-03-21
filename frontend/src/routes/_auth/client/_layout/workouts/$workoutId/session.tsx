import { createFileRoute } from '@tanstack/react-router'
import { WorkoutSession } from '@/features/workouts/components/WorkoutSession'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/client/_layout/workouts/$workoutId/session')({
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),

    component: function WorkoutSessionRoute() {
        const { workoutId } = Route.useParams()
        return <WorkoutSession workoutId={workoutId} />
    },
})
