import { createFileRoute } from '@tanstack/react-router'
import { ExerciseAnalytics } from '@/features/analytics/components/ExerciseAnalytics'
import { programsQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/analytics/')({
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),
    component: ExerciseAnalytics,
})
