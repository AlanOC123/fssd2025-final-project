import { createFileRoute } from '@tanstack/react-router'
import { WorkoutDetail } from '@/features/workouts/components/WorkoutDetail'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/client/_layout/workouts/$workoutId/')({
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),

    component: function WorkoutDetailRoute() {
        const { workoutId } = Route.useParams()
        return <WorkoutDetail workoutId={workoutId} />
    },
})
