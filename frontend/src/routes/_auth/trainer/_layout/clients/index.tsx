import { createFileRoute } from '@tanstack/react-router'
import { ClientList } from '@/features/clients/components/ClientList'
import { activeMembershipsQueryOptions } from '@/features/memberships/api'

/**
 * @fileoverview Defines the routing and data pre-fetching logic for the trainer's
 * client management section. This module ensures that active membership data
 * is populated in the query cache before the client list view is rendered.
 */

/**
 * Route configuration for the trainer's client list view.
 * Maps the base clients path within the authenticated trainer layout hierarchy.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/clients/')({
    /**
     * Pre-fetches active membership data into the TanStack Query cache.
     *
     * @param context Object containing the route context and the QueryClient.
     * @return {Promise<unknown>} A promise that resolves when the active
     * memberships are successfully cached.
     * @throws {Error} If the active memberships query fails to resolve due to
     * network or server issues.
     */
    loader: ({ context: { queryClient } }) =>
        queryClient.ensureQueryData(activeMembershipsQueryOptions()),

    component: ClientList,
})
