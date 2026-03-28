import { createFileRoute } from '@tanstack/react-router'
import { TrainerWorkoutList } from '@/features/workouts/components/TrainerWorkoutList'
import { programsQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the routing and data pre-fetching for the trainer's
 * workout management view. This module ensures that program data is available
 * in the query cache before the workout list is rendered.
 */

/**
 * Route configuration for the trainer's workout list.
 * This route is situated within the authenticated trainer layout hierarchy.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/workouts/')({
    /**
     * Pre-fetches program data into the TanStack Query cache.
     *
     * @param context Object containing the route context and the QueryClient.
     * @return {Promise<unknown>} A promise that resolves when the program data
     * has been successfully fetched and cached.
     * @throws {Error} If the programs query fails to resolve.
     */
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),

    component: TrainerWorkoutList,
})
