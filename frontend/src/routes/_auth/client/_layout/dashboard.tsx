import { createFileRoute } from '@tanstack/react-router'
import { ClientDashboard } from '@/features/dashboard/components/ClientDashboard'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/client/_layout/dashboard')({
    loader: async ({ context: { queryClient } }) => {
        const [, , programs] = await Promise.all([
            queryClient.ensureQueryData(membershipsQueryOptions({ status: 'Active' })),
            queryClient.ensureQueryData(
                membershipsQueryOptions({ status: 'Pending Trainer Review' }),
            ),
            queryClient.ensureQueryData(programsQueryOptions({ status: 'IN_PROGRESS' })),
        ])

        const activePhase = programs.results?.[0]?.remaining_phases?.[0]
        await queryClient.ensureQueryData(
            workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
        )
    },
    component: ClientDashboard,
})
