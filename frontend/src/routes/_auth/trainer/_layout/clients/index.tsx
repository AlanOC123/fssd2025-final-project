import { createFileRoute } from '@tanstack/react-router'
import { ClientList } from '@/features/clients/components/ClientList'
import { activeMembershipsQueryOptions } from '@/features/memberships/api'

export const Route = createFileRoute('/_auth/trainer/_layout/clients/')({
    loader: ({ context: { queryClient } }) =>
        queryClient.ensureQueryData(activeMembershipsQueryOptions()),

    component: ClientList,
})
