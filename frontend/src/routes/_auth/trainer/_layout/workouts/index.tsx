import { createFileRoute } from '@tanstack/react-router'
import { TrainerWorkoutList } from '@/features/workouts/components/TrainerWorkoutList'
import { programsQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/workouts/')({
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),
    component: TrainerWorkoutList,
})
