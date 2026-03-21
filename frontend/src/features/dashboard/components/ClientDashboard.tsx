import { useState } from 'react'
import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import {
    Dumbbell,
    Calendar,
    User,
    BookOpen,
    ChevronRight,
    Clock,
    UserPlus,
    LogOut,
} from 'lucide-react'
import { membershipsQueryOptions } from '@/features/memberships/api'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'
import { DissolveDialog } from '@/features/clients/components/DissolveDialog'
import type { WorkoutListItem } from '@/features/workouts/types'
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
import { ROUTES } from '@/app/constants'
import { useAuth } from '@/shared/hooks/useAuth'

// ─── Workout Row ──────────────────────────────────────────────────────────────

function WorkoutRow({ workout }: { workout: WorkoutListItem }) {
    const navigate = useNavigate()

    const date = workout.planned_date
        ? new Date(workout.planned_date).toLocaleDateString('en-IE', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
          })
        : 'No date set'

    const isToday = workout.planned_date
        ? new Date(workout.planned_date).toDateString() === new Date().toDateString()
        : false

    const isPast = workout.planned_date
        ? new Date(workout.planned_date) < new Date() && !isToday
        : false

    return (
        <Button
            variant="outline"
            onClick={() => navigate({ to: `${ROUTES.client.workouts}/${workout.id}` })}
            className="h-auto w-full justify-start gap-4 px-4 py-3 text-left"
        >
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-400 shrink-0">
                <Dumbbell size={15} />
            </div>
            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100 truncate">{workout.workout_name}</p>
                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-grey-500">
                    <Calendar size={11} />
                    <span>{date}</span>
                </div>
            </div>
            {isToday && (
                <Badge className="bg-brand-500/15 text-brand-400 border-transparent shrink-0">
                    Today
                </Badge>
            )}
            {isPast && (
                <Badge className="bg-grey-700/40 text-grey-500 border-transparent shrink-0">
                    Due
                </Badge>
            )}
            <ChevronRight size={15} className="text-grey-600 shrink-0" />
        </Button>
    )
}

// ─── No Membership State ──────────────────────────────────────────────────────

function NoMembershipState() {
    const navigate = useNavigate()
    return (
        <Empty className="border border-dashed border-grey-800 mt-4">
            <EmptyHeader>
                <EmptyMedia variant="icon">
                    <UserPlus />
                </EmptyMedia>
                <EmptyTitle className="text-base text-grey-200">Find a trainer</EmptyTitle>
                <EmptyDescription className="text-sm">
                    Connect with a trainer to get a personalised program and start tracking your
                    workouts.
                </EmptyDescription>
            </EmptyHeader>
            <Button onClick={() => navigate({ to: ROUTES.client.findTrainer })} className="gap-2">
                <UserPlus size={15} />
                Find a Trainer
            </Button>
        </Empty>
    )
}

// ─── Pending Membership State ─────────────────────────────────────────────────

function PendingMembershipState({ trainerName }: { trainerName: string }) {
    return (
        <div className="flex items-start gap-4 px-4 py-4 rounded-xl bg-warning-500/5 border border-warning-500/20 mt-4">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-warning-500/10 text-warning-400 shrink-0 mt-0.5">
                <Clock size={18} />
            </div>
            <div>
                <p className="text-sm font-medium text-grey-100">Request pending</p>
                <p className="text-sm text-grey-400 mt-0.5">
                    Waiting for <span className="text-grey-200">{trainerName}</span> to accept your
                    request.
                </p>
            </div>
        </div>
    )
}

// ─── Client Dashboard ─────────────────────────────────────────────────────────

export function ClientDashboard() {
    const { user } = useAuth()
    const navigate = useNavigate()
    const [dissolveOpen, setDissolveOpen] = useState(false)

    const { data: activeMemberships } = useSuspenseQuery(
        membershipsQueryOptions({ status: 'Active' }),
    )
    const { data: pendingMemberships } = useSuspenseQuery(
        membershipsQueryOptions({ status: 'Pending Trainer Review' }),
    )
    const { data: programs } = useSuspenseQuery(programsQueryOptions({ status: 'IN_PROGRESS' }))

    const activeMembership = activeMemberships.results[0] ?? null
    const pendingMembership = pendingMemberships.results[0] ?? null
    const activeProgram = programs.results[0] ?? null
    const activePhase = activeProgram?.remaining_phases?.[0] ?? null

    const { data: workouts } = useSuspenseQuery(
        workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
    )

    const upcomingWorkouts = workouts.results
        .filter(
            (w) =>
                w.planned_date &&
                new Date(w.planned_date) >= new Date(new Date().setHours(0, 0, 0, 0)),
        )
        .sort((a, b) => new Date(a.planned_date!).getTime() - new Date(b.planned_date!).getTime())
        .slice(0, 5)

    const overdueWorkouts = workouts.results
        .filter(
            (w) =>
                w.planned_date &&
                new Date(w.planned_date) < new Date(new Date().setHours(0, 0, 0, 0)),
        )
        .sort((a, b) => new Date(b.planned_date!).getTime() - new Date(a.planned_date!).getTime())
        .slice(0, 3)

    const hasNoMembership = !activeMembership && !pendingMembership

    return (
        <div className="p-6 max-w-2xl mx-auto">
            {/* Greeting */}
            <div className="mb-8">
                <h1 className="text-2xl font-semibold text-grey-50">
                    Hey, {user?.first_name ?? 'Athlete'} 👋
                </h1>
                <p className="text-sm text-grey-400 mt-1">Here's your training overview.</p>
            </div>

            {/* State 1 — No membership */}
            {hasNoMembership && <NoMembershipState />}

            {/* State 2 — Pending */}
            {pendingMembership && !activeMembership && (
                <PendingMembershipState trainerName={pendingMembership.trainer_name} />
            )}

            {/* State 3 — Active */}
            {activeMembership && (
                <>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
                        {/* Trainer card */}
                        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-grey-900 border border-grey-800">
                            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 shrink-0">
                                <User size={15} />
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs text-grey-500">Trainer</p>
                                <p className="text-sm font-medium text-grey-100 truncate">
                                    {activeMembership.trainer_name}
                                </p>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon-sm"
                                onClick={() => setDissolveOpen(true)}
                                className="text-grey-600 hover:text-danger-400 hover:bg-danger-500/10 shrink-0"
                                aria-label="Leave trainer"
                            >
                                <LogOut size={14} />
                            </Button>
                        </div>

                        {/* Program card */}
                        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-grey-900 border border-grey-800">
                            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-brand-500/10 text-brand-400 shrink-0">
                                <BookOpen size={15} />
                            </div>
                            <div className="min-w-0">
                                <p className="text-xs text-grey-500">Active program</p>
                                <p className="text-sm font-medium text-grey-100 truncate">
                                    {activeProgram
                                        ? activeProgram.program_name
                                        : 'No active program'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <Separator className="bg-grey-800 mb-8" />

                    {/* Workouts */}
                    {!activeProgram || !activePhase ? (
                        <Empty className="border border-dashed border-grey-800">
                            <EmptyHeader>
                                <EmptyMedia variant="icon">
                                    <Dumbbell />
                                </EmptyMedia>
                                <EmptyTitle className="text-sm text-grey-300">
                                    No workouts yet
                                </EmptyTitle>
                                <EmptyDescription className="text-xs">
                                    Your trainer will assign workouts once your program is active.
                                </EmptyDescription>
                            </EmptyHeader>
                        </Empty>
                    ) : (
                        <>
                            {overdueWorkouts.length > 0 && (
                                <div className="mb-6">
                                    <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                                        Overdue
                                    </p>
                                    <div className="flex flex-col gap-2">
                                        {overdueWorkouts.map((w) => (
                                            <WorkoutRow key={w.id} workout={w} />
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div>
                                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                                    Upcoming
                                </p>
                                {upcomingWorkouts.length === 0 ? (
                                    <Empty className="border border-dashed border-grey-800 py-8">
                                        <EmptyHeader>
                                            <EmptyTitle className="text-sm text-grey-500">
                                                No upcoming workouts
                                            </EmptyTitle>
                                        </EmptyHeader>
                                    </Empty>
                                ) : (
                                    <div className="flex flex-col gap-2">
                                        {upcomingWorkouts.map((w) => (
                                            <WorkoutRow key={w.id} workout={w} />
                                        ))}
                                    </div>
                                )}
                            </div>
                            <div className="mt-4 flex justify-end">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => navigate({ to: ROUTES.client.workouts })}
                                    className="text-grey-500 hover:text-grey-200"
                                >
                                    View all workouts
                                    <ChevronRight size={14} />
                                </Button>
                            </div>
                        </>
                    )}

                    {/* Dissolve dialog */}
                    <DissolveDialog
                        membershipId={activeMembership.id}
                        trainerName={activeMembership.trainer_name}
                        open={dissolveOpen}
                        onOpenChange={setDissolveOpen}
                    />
                </>
            )}
        </div>
    )
}
