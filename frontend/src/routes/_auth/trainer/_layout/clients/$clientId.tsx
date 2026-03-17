import { createFileRoute } from '@tanstack/react-router'
import { ClientDetail } from '@/features/clients/components/ClientDetail'
import { membershipDetailQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/clients/$clientId')({
    loader: ({ context: { queryClient }, params: { clientId } }) =>
        Promise.all([
            queryClient.ensureQueryData(membershipDetailQueryOptions(clientId)),
            queryClient.ensureQueryData(
                programsQueryOptions({ trainer_client_membership: clientId }),
            ),
        ]),

    component: function ClientDetailRoute() {
        const { clientId } = Route.useParams()
        return <ClientDetail membershipId={clientId} />
    },
})
