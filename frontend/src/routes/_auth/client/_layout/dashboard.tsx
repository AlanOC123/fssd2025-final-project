import { createFileRoute } from '@tanstack/react-router'
import { ClientDashboard } from '@/features/dashboard/components/ClientDashboard'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'

/**
 * @fileoverview Defines the dashboard route for authenticated clients.
 * This route handles the coordination of multiple data fetches required
 * to display a complete overview of the client's current fitness status.
 */

/**
 * Route configuration for the client dashboard.
 * Orchestrates pre-fetching of membership and program data to ensure
 * the UI has immediate access to critical state upon navigation.
 */
export const Route = createFileRoute('/_auth/client/_layout/dashboard')({
    /**
     * Hydrates the query cache with membership, program, and workout data.
     * * It concurrently fetches active and pending memberships along with
     * programs in progress. Once the primary program data is available,
     * it identifies the active phase to fetch specific workout details.
     *
     * @param context The route context containing the QueryClient.
     * @return {Promise<void>} Resolves when all critical dashboard data has been
     * successfully fetched or cached.
     * @throws {Error} If the underlying network requests for memberships or
     * programs fail and no cached data is available.
     */
    loader: async ({ context: { queryClient } }) => {
        // Perform initial data fetching for memberships and programs in parallel.
        const [, , programs] = await Promise.all([
            queryClient.ensureQueryData(membershipsQueryOptions({ status: 'Active' })),
            queryClient.ensureQueryData(
                membershipsQueryOptions({ status: 'Pending Trainer Review' }),
            ),
            queryClient.ensureQueryData(programsQueryOptions({ status: 'IN_PROGRESS' })),
        ])

        // Extract the current workout phase from the first active program results.
        const activePhase = programs.results?.[0]?.remaining_phases?.[0]

        // Fetch associated workouts if an active phase exists.
        await queryClient.ensureQueryData(
            workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
        )
    },
    component: ClientDashboard,
})
