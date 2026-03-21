import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, UserPlus, ArrowLeft, Building2, Target } from 'lucide-react'
import { trainersApi, trainersQueryOptions, TRAINERS_QUERY_KEY } from '@/features/trainers/api'
import { MEMBERSHIP_QUERY_KEY } from '@/features/memberships/api'
import type { TrainerMatchProfile } from '@/features/trainers/types'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Badge } from '@/shared/components/ui/badge'
import { Avatar, AvatarFallback } from '@/shared/components/ui/avatar'
import { Separator } from '@/shared/components/ui/separator'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { toast, toastApiError } from '@/shared/utils/toast'
import { useDebounce } from '@/shared/hooks/useDebounce'
import { ROUTES } from '@/app/constants'

// ─── Trainer Card ─────────────────────────────────────────────────────────────

function TrainerCard({ trainer }: { trainer: TrainerMatchProfile }) {
    const queryClient = useQueryClient()

    const initials = `${trainer.first_name[0] ?? ''}${trainer.last_name[0] ?? ''}`.toUpperCase()
    const fullName = `${trainer.first_name} ${trainer.last_name}`.trim()

    const requestMutation = useMutation({
        mutationFn: () => trainersApi.requestMembership(trainer.id),
        onSuccess: () => {
            toast.success('Request sent!', {
                description: `Your request has been sent to ${fullName}.`,
            })
            // Invalidate both trainers list (removes this trainer) and memberships
            queryClient.invalidateQueries({ queryKey: TRAINERS_QUERY_KEY })
            queryClient.invalidateQueries({ queryKey: MEMBERSHIP_QUERY_KEY() })
        },
        onError: (error) => toastApiError(error, 'Failed to send request'),
    })

    console.log(trainer)

    return (
        <div className="flex items-start gap-4 px-4 py-4 rounded-xl bg-grey-900 border border-grey-800">
            <Avatar size="lg" className="shrink-0">
                <AvatarFallback className="bg-brand-800 text-brand-200 font-semibold">
                    {initials}
                </AvatarFallback>
            </Avatar>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-grey-100">{fullName}</p>

                {trainer.company && (
                    <div className="flex items-center gap-1.5 mt-0.5 text-xs text-grey-500">
                        <Building2 size={11} />
                        <span>{trainer.company}</span>
                    </div>
                )}

                {(trainer.accepted_goals.length > 0 || trainer.accepted_levels.length > 0) && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                        {trainer.accepted_goals.map((g) => (
                            <Badge
                                key={g.id}
                                className="bg-brand-500/10 text-brand-400 border-transparent text-xs"
                            >
                                {g.label}
                            </Badge>
                        ))}
                        {trainer.accepted_levels.map((l) => (
                            <Badge
                                key={l.id}
                                className="bg-grey-700/40 text-grey-400 border-transparent text-xs"
                            >
                                {l.label}
                            </Badge>
                        ))}
                    </div>
                )}
            </div>

            <Button
                size="sm"
                onClick={() => requestMutation.mutate()}
                disabled={requestMutation.isPending || requestMutation.isSuccess}
                className="shrink-0 gap-1.5"
            >
                <UserPlus size={13} />
                {requestMutation.isSuccess
                    ? 'Requested'
                    : requestMutation.isPending
                      ? 'Sending...'
                      : 'Request'}
            </Button>
        </div>
    )
}

// ─── Find Trainer ─────────────────────────────────────────────────────────────

export function FindTrainer() {
    const navigate = useNavigate()
    const [search, setSearch] = useState('')
    const debouncedSearch = useDebounce(search, 300)

    const { data, isLoading } = useQuery(trainersQueryOptions(debouncedSearch || ''))

    const trainers = data?.results ?? []

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate({ to: ROUTES.client.dashboard })}
                className="mb-6 -ml-2 text-grey-500 hover:text-grey-200"
            >
                <ArrowLeft size={15} />
                Dashboard
            </Button>

            <div className="mb-6">
                <h1 className="text-2xl font-semibold text-grey-50">Find a Trainer</h1>
                <p className="text-sm text-grey-400 mt-1">
                    Trainers matched to your goals and experience level.
                </p>
            </div>

            {/* Search */}
            <div className="relative mb-6">
                <Search
                    size={15}
                    className="absolute left-3 top-1/2 -translate-y-1/2 text-grey-500"
                />
                <Input
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search by name or company..."
                    className="pl-9"
                />
            </div>

            <Separator className="bg-grey-800 mb-6" />

            {isLoading ? (
                <div className="flex items-center justify-center py-12">
                    <div className="size-5 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
                </div>
            ) : trainers.length === 0 ? (
                <Empty className="border border-dashed border-grey-800">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Target />
                        </EmptyMedia>
                        <EmptyTitle className="text-sm text-grey-300">No trainers found</EmptyTitle>
                        <EmptyDescription className="text-xs">
                            {search
                                ? 'Try a different search term.'
                                : 'No trainers are currently available for your goal and level.'}
                        </EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : (
                <div className="flex flex-col gap-3">
                    {trainers.map((trainer) => (
                        <TrainerCard key={trainer.id} trainer={trainer} />
                    ))}
                </div>
            )}
        </div>
    )
}
