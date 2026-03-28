import { createFileRoute } from '@tanstack/react-router'
import { TrainerDashboard } from '@/features/dashboard/components/TrainerDashboard'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { activeProgramsQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the routing and data pre-fetching logic for the trainer
 * dashboard. This module ensures all critical business metrics and lists are
 * available in the cache before the dashboard renders.
 */

/**
 * Route definition for the trainer dashboard.
 * Maps the '/dashboard' endpoint within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/dashboard')({
    /**
     * Loader function to pre-fetch memberships and active programs.
     *
     * @param context Object containing the route context and query client.
     * @return {Promise<unknown[]>} A promise that resolves when all parallel
     * data queries have been initiated and cached.
     * @throws {Error} If any of the critical data fetches fail.
     */
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
