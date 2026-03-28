import { createFileRoute } from '@tanstack/react-router'
import { ClientDetail } from '@/features/clients/components/ClientDetail'
import { membershipDetailQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the route for the trainer's detailed client view.
 * This module manages the parallel fetching of membership details and
 * associated programs for a specific client identifier.
 */

/**
 * Route definition for the trainer's client detail page.
 * Maps the dynamic '$clientId' path within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/clients/$clientId')({
    /**
     * Pre-fetches client membership and program data into the TanStack Query cache.
     *
     * @param {Object} args The loader arguments.
     * @param {Object} args.context Object containing the route context and the QueryClient.
     * @param {Object} args.params Object containing route parameters, specifically the clientId.
     * @return {!Promise<!Array<unknown>>} A promise that resolves when both
     * the membership detail and programs queries are successfully cached.
     * @throws {!Error} If either underlying query fails to resolve.
     */
    loader: ({ context: { queryClient }, params: { clientId } }) =>
        Promise.all([
            queryClient.ensureQueryData(membershipDetailQueryOptions(clientId)),
            queryClient.ensureQueryData(
                programsQueryOptions({ trainer_client_membership: clientId }),
            ),
        ]),

    /**
     * Functional component serving as the entry point for the client detail view.
     * * @return {JSX.Element} The rendered client detail component.
     */
    component: function ClientDetailRoute() {
        // Extracts the clientId from the route parameters and passes it as the
        // membershipId to the ClientDetail component.
        const { clientId } = Route.useParams()
        return <ClientDetail membershipId={clientId} />
    },
})
