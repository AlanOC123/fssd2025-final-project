import { createFileRoute } from '@tanstack/react-router'
import { WorkoutList } from '@/features/workouts/components/WorkoutList'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'

/**
 * @fileoverview Defines the routing for the client's workout list.
 * This module handles the pre-fetching of active program phases and their
 * corresponding workout schedules before the view is rendered.
 */

/**
 * Route configuration for the client workouts page.
 * Maps the workout list endpoint within the authenticated client layout.
 */
export const Route = createFileRoute('/_auth/client/_layout/workouts/')({
    /**
     * Pre-fetches necessary workout and program data to populate the query cache.
     *
     * @param context Object containing the TanStack Query client.
     * @return {Promise<void>} Resolves when the required data is cached.
     * @throws {Error} If the program or workout query fails to resolve.
     */
    loader: async ({ context: { queryClient } }) => {
        // Retrieves programs currently in progress to identify the active phase.
        const programs = await queryClient.ensureQueryData(
            programsQueryOptions({ status: 'IN_PROGRESS' }),
        )

        // Selects the first available phase from the current program to fetch workouts.
        const activePhase = programs.results[0]?.remaining_phases?.[0]

        await queryClient.ensureQueryData(
            workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
        )
    },

    component: WorkoutList,
})
