import { useSuspenseQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft, BookOpen, Calendar, AlertTriangle } from 'lucide-react'
import {
    membershipDetailQueryOptions,
    membershipsApi,
    MEMBERSHIP_QUERY_KEY,
} from '@/features/clients'
import { programsQueryOptions, PROGRAM_QUERY_KEY } from '@/features/programs/api'
import type { ProgramListItem } from '@/features/programs/types'
import { toast, toastApiError } from '@/shared/utils/toast'
import { Avatar, AvatarFallback } from '@/shared/components/ui/avatar'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import { Separator } from '@/shared/components/ui/separator'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'

// ─── Status config ────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<string, string> = {
    CREATING: 'bg-grey-700/40 text-grey-400 border-transparent',
    OUT_FOR_REVIEW: 'bg-info-500/10 text-info-400 border-transparent',
    READY_TO_BEGIN: 'bg-warning-500/10 text-warning-400 border-transparent',
    IN_PROGRESS: 'bg-success-500/10 text-success-400 border-transparent',
    COMPLETED: 'bg-brand-500/10 text-brand-400 border-transparent',
    ABANDONED: 'bg-danger-500/10 text-danger-400 border-transparent',
}

// ─── Program Row ──────────────────────────────────────────────────────────────

function ProgramRow({ program }: { program: ProgramListItem }) {
    const statusStyle = STATUS_STYLES[program.status.code] ?? STATUS_STYLES.CREATING

    return (
        <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-grey-900 border border-grey-800">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-400 shrink-0">
                <BookOpen size={15} />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100 truncate">{program.program_name}</p>
                <p className="text-xs text-grey-500 mt-0.5">
                    {program.training_goal.label} · {program.experience_level.label}
                </p>
            </div>
            <Badge className={cn('shrink-0', statusStyle)}>{program.status.label}</Badge>
        </div>
    )
}

// ─── Dissolve Button ─────────────────────────────────────────────────────────

function DissolveButton({
    membershipId,
    clientName,
}: {
    membershipId: string
    clientName: string
}) {
    const navigate = useNavigate()
    const queryClient = useQueryClient()

    const dissolveMutation = useMutation({
        mutationFn: () => membershipsApi.dissolve(membershipId),
        onSuccess: () => {
            toast.success('Membership dissolved', {
                description: `${clientName} has been removed from your clients.`,
            })
            queryClient.invalidateQueries({ queryKey: MEMBERSHIP_QUERY_KEY() })
            queryClient.invalidateQueries({ queryKey: PROGRAM_QUERY_KEY() })
            navigate({ to: ROUTES.trainer.clients })
        },
        onError: (error) => toastApiError(error, 'Failed to dissolve membership'),
    })

    return (
        <Button
            variant="destructive"
            size="sm"
            onClick={() => dissolveMutation.mutate()}
            disabled={dissolveMutation.isPending}
        >
            <AlertTriangle size={14} />
            {dissolveMutation.isPending ? 'Dissolving...' : 'Dissolve membership'}
        </Button>
    )
}

// ─── Client Detail ───────────────────────────────────────────────────────────

export function ClientDetail({ membershipId }: { membershipId: string }) {
    const navigate = useNavigate()

    const { data: membership } = useSuspenseQuery(membershipDetailQueryOptions(membershipId))
    const { data: programs } = useSuspenseQuery(
        programsQueryOptions({ trainer_client_membership: membershipId }),
    )

    const initials = membership.client_name
        .split(' ')
        .map((n) => n[0] ?? '')
        .join('')
        .toUpperCase()
        .slice(0, 2)

    const startedAt = membership.started_at
        ? new Date(membership.started_at).toLocaleDateString('en-IE', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
          })
        : '—'

    const activePrograms = programs.results.filter((p) => p.status.code === 'IN_PROGRESS')
    const otherPrograms = programs.results.filter((p) => p.status.code !== 'IN_PROGRESS')

    return (
        <div className="p-8 max-w-3xl w-full">
            {/* Back */}
            <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate({ to: ROUTES.trainer.clients })}
                className="mb-6 -ml-2 text-grey-500 hover:text-grey-200"
            >
                <ArrowLeft size={15} />
                Clients
            </Button>

            {/* Client header */}
            <div className="flex items-center gap-4 mb-8">
                <Avatar size="lg" className="shrink-0 bg-brand-800 w-14 h-14">
                    <AvatarFallback className="bg-brand-800 text-brand-200 text-lg font-semibold">
                        {initials}
                    </AvatarFallback>
                </Avatar>

                <div className="flex-1 min-w-0">
                    <h1 className="text-2xl font-semibold text-grey-50">
                        {membership.client_name}
                    </h1>
                    <div className="flex items-center gap-1.5 mt-1 text-xs text-grey-500">
                        <Calendar size={12} />
                        <span>Client since {startedAt}</span>
                    </div>
                </div>

                <DissolveButton membershipId={membershipId} clientName={membership.client_name} />
            </div>

            <Separator className="bg-grey-800 mb-8" />

            {/* Programs */}
            <section>
                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                    Programs
                    {programs.count > 0 && (
                        <span className="ml-2 text-grey-600 normal-case tracking-normal">
                            ({programs.count})
                        </span>
                    )}
                </p>

                {programs.count === 0 ? (
                    <Empty className="border border-dashed border-grey-800 py-8">
                        <EmptyHeader>
                            <EmptyMedia variant="icon">
                                <BookOpen />
                            </EmptyMedia>
                            <EmptyTitle className="text-sm text-grey-500">
                                No programs yet
                            </EmptyTitle>
                            <EmptyDescription className="text-xs">
                                Create a program for this client from the Programs page.
                            </EmptyDescription>
                        </EmptyHeader>
                    </Empty>
                ) : (
                    <div className="flex flex-col gap-2">
                        {activePrograms.map((p) => (
                            <ProgramRow key={p.id} program={p} />
                        ))}
                        {activePrograms.length > 0 && otherPrograms.length > 0 && (
                            <p className="text-xs text-grey-600 mt-2 mb-1">Previous</p>
                        )}
                        {otherPrograms.map((p) => (
                            <ProgramRow key={p.id} program={p} />
                        ))}
                    </div>
                )}
            </section>
        </div>
    )
}
