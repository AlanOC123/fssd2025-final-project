import { createFileRoute } from '@tanstack/react-router'
import { ProgramList } from '@/features/programs/components/ProgramList'
import { programsQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the routing and data pre-fetching logic for the trainer's
 * program management dashboard. This module ensures that the program list data
 * is populated in the cache before the user navigates to the view.
 */

/**
 * Route configuration for the trainer's program list view.
 * Maps the base programs endpoint within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/programs/')({
    /**
     * Pre-fetches the list of programs into the TanStack Query cache.
     *
     * @param context Object containing the route context and the QueryClient instance.
     * @return {Promise<unknown>} A promise that resolves when the program data has
     * been successfully fetched and cached.
     * @throws {Error} If the programs query fails to resolve due to network or
     * server issues.
     */
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),

    component: ProgramList,
})
