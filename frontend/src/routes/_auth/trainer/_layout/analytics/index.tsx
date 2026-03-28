import { createFileRoute } from '@tanstack/react-router'
import { ExerciseAnalytics } from '@/features/analytics/components/ExerciseAnalytics'
import { programsQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the route configuration for trainer-side exercise
 * analytics. This module handles the data pre-fetching of program information
 * required to generate analytical visualizations.
 */

/**
 * Route configuration for the trainer exercise analytics page.
 * Maps the '/analytics' path within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/analytics/')({
    /**
     * Loader function to pre-fetch program data for analytics.
     *
     * @param context Object containing the route context and query client.
     * @return {Promise<unknown>} A promise that resolves when the program query
     * data is cached.
     * @throws {Error} If the program query fails to resolve.
     */
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),

    component: ExerciseAnalytics,
})
