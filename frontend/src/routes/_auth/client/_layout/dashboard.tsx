import { createFileRoute } from '@tanstack/react-router'
import { ClientDashboard } from '@/features/dashboard/components/ClientDashboard'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'

export const Route = createFileRoute('/_auth/client/_layout/dashboard')({
    loader: async ({ context: { queryClient } }) => {
        // Load memberships and programs in parallel
        const [, programs] = await Promise.all([
            queryClient.ensureQueryData(membershipsQueryOptions({ status: 'Active' })),
            queryClient.ensureQueryData(programsQueryOptions({ status: 'IN_PROGRESS' })),
        ])

        // Load workouts for the first active phase if one exists
        const activePhase = programs.results?.[0]?.remaining_phases?.[0]
        if (activePhase) {
            await queryClient.ensureQueryData(
                workoutsQueryOptions({ program_phase: activePhase.id }),
            )
        } else {
            await queryClient.ensureQueryData(workoutsQueryOptions())
        }
    },

    component: ClientDashboard,
})
