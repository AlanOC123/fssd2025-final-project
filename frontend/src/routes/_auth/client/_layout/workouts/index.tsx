import { createFileRoute } from '@tanstack/react-router'
import { WorkoutList } from '@/features/workouts/components/WorkoutList'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/client/_layout/workouts/')({
    loader: async ({ context: { queryClient } }) => {
        const programs = await queryClient.ensureQueryData(
            programsQueryOptions({ status: 'IN_PROGRESS' }),
        )
        const activePhase = programs.results[0]?.remaining_phases?.[0]
        await queryClient.ensureQueryData(
            workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
        )
    },

    component: WorkoutList,
})
