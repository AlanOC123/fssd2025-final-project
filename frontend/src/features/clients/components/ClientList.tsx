import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { UserX, ChevronRight, Users } from 'lucide-react'
import { activeMembershipsQueryOptions } from '@/features/clients'
import type { Membership } from '@/features/clients'
import { Avatar, AvatarFallback } from '@/shared/components/ui/avatar'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { ROUTES } from '@/app/constants'

// ─── Client Row ──────────────────────────────────────────────────────────────

function ClientRow({ membership }: { membership: Membership }) {
    const navigate = useNavigate()

    const initials = membership.client_name
        .split(' ')
        .map((n) => n[0] ?? '')
        .join('')
        .toUpperCase()
        .slice(0, 2)

    const startedAt = membership.started_at
        ? new Date(membership.started_at).toLocaleDateString('en-IE', {
              day: 'numeric',
              month: 'short',
              year: 'numeric',
          })
        : '—'

    return (
        <Button
            variant="outline"
            onClick={() => navigate({ to: `${ROUTES.trainer.clients}/${membership.id}` })}
            className="h-auto w-full justify-start gap-4 px-4 py-3 text-left"
        >
            <Avatar size="default" className="shrink-0 bg-brand-800">
                <AvatarFallback className="bg-brand-800 text-brand-200 text-xs font-semibold">
                    {initials}
                </AvatarFallback>
            </Avatar>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100 truncate">
                    {membership.client_name}
                </p>
                <p className="text-xs text-grey-500 mt-0.5">Client since {startedAt}</p>
            </div>

            <Badge className="bg-success-500/10 text-success-400 border-transparent shrink-0">
                Active
            </Badge>

            <ChevronRight size={15} className="text-grey-600 shrink-0" />
        </Button>
    )
}

// ─── Empty State ─────────────────────────────────────────────────────────────

function EmptyClients() {
    return (
        <Empty className="border border-dashed border-grey-800 min-h-64 w-full">
            <EmptyHeader>
                <EmptyMedia variant="icon">
                    <UserX />
                </EmptyMedia>
                <EmptyTitle className="text-sm text-grey-300">No active clients</EmptyTitle>
                <EmptyDescription className="text-xs">
                    Clients will appear here once they request a membership and you accept it.
                </EmptyDescription>
            </EmptyHeader>
        </Empty>
    )
}

// ─── Client List ─────────────────────────────────────────────────────────────

export function ClientList() {
    const { data: memberships } = useSuspenseQuery(activeMembershipsQueryOptions())

    return (
        <div className="p-8 w-full">
            <div className="flex items-center gap-3 mb-8">
                <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400">
                    <Users size={18} />
                </div>
                <div>
                    <h1 className="text-2xl font-semibold text-grey-50">Clients</h1>
                    <p className="text-sm text-grey-400 mt-0.5">
                        {memberships.count}{' '}
                        {memberships.count === 1 ? 'active client' : 'active clients'}
                    </p>
                </div>
            </div>

            {memberships.count === 0 ? (
                <EmptyClients />
            ) : (
                <div className="flex flex-col gap-2">
                    {memberships.results.map((m) => (
                        <ClientRow key={m.id} membership={m} />
                    ))}
                </div>
            )}
        </div>
    )
}
