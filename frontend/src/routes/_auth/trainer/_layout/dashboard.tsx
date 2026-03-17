import { createFileRoute } from '@tanstack/react-router'
import { TrainerDashboard } from '@/features/dashboard/components/TrainerDashboard'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { activeProgramsQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/dashboard')({
    loader: ({ context: { queryClient } }) =>
        Promise.all([
            queryClient.ensureQueryData(membershipsQueryOptions({ status: 'Active' })),
            queryClient.ensureQueryData(
                membershipsQueryOptions({ status: 'Pending Trainer Review' }),
            ),
            queryClient.ensureQueryData(activeProgramsQueryOptions()),
        ]),

    component: TrainerDashboard,
})
