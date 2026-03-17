import { useSuspenseQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { Users, BookOpen, Clock, CheckCircle, XCircle, ChevronRight } from 'lucide-react'
import { membershipsQueryOptions, membershipsApi } from '@/features/memberships/api'
import { activeProgramsQueryOptions } from '@/features/programs/api'
import type { Membership } from '@/features/memberships/types'
import { toast } from '@/shared/utils/toast'
import { toastApiError } from '@/shared/utils/toast'
import { ROUTES } from '@/app/constants'
import { cn } from '@/shared/utils/utils'
import { MEMBERSHIP_QUERY_KEY } from '@/features/memberships/api'

// ─── Stat Card ───────────────────────────────────────────────────────────────

interface StatCardProps {
    label: string
    value: number
    icon: React.ElementType
    onClick?: () => void
    accent?: 'brand' | 'warning'
}

function StatCard({ label, value, icon: Icon, onClick, accent = 'brand' }: StatCardProps) {
    const Wrapper = onClick ? 'button' : 'div'

    return (
        <Wrapper
            onClick={onClick}
            className={cn(
                'flex items-center gap-4 rounded-xl bg-grey-900 border border-grey-800 p-5 text-left w-full',
                onClick &&
                    'cursor-pointer hover:border-grey-700 hover:bg-grey-800/60 transition-all duration-200',
            )}
        >
            <div
                className={cn(
                    'flex items-center justify-center w-10 h-10 rounded-lg shrink-0',
                    accent === 'brand'
                        ? 'bg-brand-500/10 text-brand-400'
                        : 'bg-warning-500/10 text-warning-400',
                )}
            >
                <Icon size={18} />
            </div>
            <div className="min-w-0">
                <p className="text-2xl font-semibold text-grey-50 leading-none">{value}</p>
                <p className="text-sm text-grey-400 mt-1">{label}</p>
            </div>
            {onClick && <ChevronRight size={16} className="ml-auto text-grey-600 shrink-0" />}
        </Wrapper>
    )
}

// ─── Pending Request Row ─────────────────────────────────────────────────────

function PendingRequestRow({ membership }: { membership: Membership }) {
    const queryClient = useQueryClient()

    const acceptMutation = useMutation({
        mutationFn: () => membershipsApi.accept(membership.id),
        onSuccess: () => {
            toast.success('Request accepted', {
                description: `${membership.client_name} is now your client.`,
            })
            queryClient.invalidateQueries({ queryKey: MEMBERSHIP_QUERY_KEY() })
        },
        onError: (error) => toastApiError(error, 'Failed to accept request'),
    })

    const rejectMutation = useMutation({
        mutationFn: () => membershipsApi.reject(membership.id),
        onSuccess: () => {
            toast.info('Request declined')
            queryClient.invalidateQueries({ queryKey: MEMBERSHIP_QUERY_KEY() })
        },
        onError: (error) => toastApiError(error, 'Failed to decline request'),
    })

    const isPending = acceptMutation.isPending || rejectMutation.isPending

    return (
        <div className="flex items-center gap-3 py-3 px-4 rounded-lg bg-grey-900 border border-grey-800">
            {/* Avatar */}
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-grey-700 text-grey-300 text-xs font-semibold shrink-0 select-none">
                {membership.client_name.charAt(0).toUpperCase()}
            </div>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100 truncate">
                    {membership.client_name}
                </p>
                <p className="text-xs text-grey-500 mt-0.5">
                    Requested{' '}
                    {new Date(membership.requested_at).toLocaleDateString('en-IE', {
                        day: 'numeric',
                        month: 'short',
                    })}
                </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
                <button
                    onClick={() => rejectMutation.mutate()}
                    disabled={isPending}
                    className="flex items-center justify-center w-8 h-8 rounded-lg text-grey-500 hover:text-danger-400 hover:bg-danger-500/10 transition-all duration-200 disabled:opacity-40 disabled:pointer-events-none cursor-pointer"
                    aria-label={`Decline ${membership.client_name}`}
                >
                    <XCircle size={16} />
                </button>
                <button
                    onClick={() => acceptMutation.mutate()}
                    disabled={isPending}
                    className="flex items-center justify-center w-8 h-8 rounded-lg text-grey-500 hover:text-success-400 hover:bg-success-500/10 transition-all duration-200 disabled:opacity-40 disabled:pointer-events-none cursor-pointer"
                    aria-label={`Accept ${membership.client_name}`}
                >
                    <CheckCircle size={16} />
                </button>
            </div>
        </div>
    )
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export function TrainerDashboard() {
    const navigate = useNavigate()

    const { data: activeMembers } = useSuspenseQuery(membershipsQueryOptions({ status: 'Active' }))
    const { data: pendingMembers } = useSuspenseQuery(
        membershipsQueryOptions({ status: 'Pending Trainer Review' }),
    )
    const { data: activePrograms } = useSuspenseQuery(activeProgramsQueryOptions())

    const hasPending = pendingMembers.count > 0

    return (
        <div className="p-8 max-w-4xl">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-grey-50">Dashboard</h1>
                <p className="text-sm text-grey-400 mt-1">Your training overview</p>
            </div>

            {/* Stats row */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <StatCard
                    label="Active clients"
                    value={activeMembers.count}
                    icon={Users}
                    onClick={() => navigate({ to: ROUTES.trainer.clients })}
                />
                <StatCard
                    label="Active programs"
                    value={activePrograms.count}
                    icon={BookOpen}
                    onClick={() => navigate({ to: ROUTES.trainer.programs })}
                />
                <StatCard
                    label="Pending requests"
                    value={pendingMembers.count}
                    icon={Clock}
                    accent={hasPending ? 'warning' : 'brand'}
                />
            </div>

            {/* Pending requests */}
            {hasPending && (
                <section>
                    <h2 className="text-sm font-medium text-grey-400 uppercase tracking-wider mb-3">
                        Pending requests
                    </h2>
                    <div className="flex flex-col gap-2">
                        {pendingMembers.results.map((m) => (
                            <PendingRequestRow key={m.id} membership={m} />
                        ))}
                    </div>
                </section>
            )}
        </div>
    )
}
