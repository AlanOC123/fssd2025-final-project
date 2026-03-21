import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { Dumbbell, Calendar, ChevronRight, CheckCircle } from 'lucide-react'
import { programsQueryOptions } from '@/features/programs/api'
import { workoutsQueryOptions } from '@/features/workouts/api'
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
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'

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

    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const plannedDate = workout.planned_date ? new Date(workout.planned_date) : null
    const isToday = plannedDate?.toDateString() === new Date().toDateString()
    const isUpcoming = plannedDate ? plannedDate >= today : false

    return (
        <Button
            variant="outline"
            onClick={() => navigate({ to: `${ROUTES.client.workouts}/${workout.id}` })}
            className="h-auto w-full justify-start gap-4 px-4 py-3 text-left"
        >
            <div
                className={cn(
                    'flex items-center justify-center w-8 h-8 rounded-lg shrink-0',
                    workout.has_session
                        ? 'bg-success-500/10 text-success-400'
                        : 'bg-grey-800 text-grey-400',
                )}
            >
                {workout.has_session ? <CheckCircle size={15} /> : <Dumbbell size={15} />}
            </div>

            <div className="flex-1 min-w-0">
                <p
                    className={cn(
                        'text-sm font-medium truncate',
                        workout.has_session ? 'text-grey-400' : 'text-grey-100',
                    )}
                >
                    {workout.workout_name}
                </p>
                <div className="flex items-center gap-1.5 mt-0.5 text-xs text-grey-500">
                    <Calendar size={11} />
                    <span>{date}</span>
                </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
                {workout.has_session && (
                    <Badge className="bg-success-500/10 text-success-400 border-transparent">
                        Done
                    </Badge>
                )}
                {!workout.has_session && isToday && (
                    <Badge className="bg-brand-500/15 text-brand-400 border-transparent">
                        Today
                    </Badge>
                )}
                {!workout.has_session && isUpcoming && !isToday && (
                    <Badge className="bg-grey-700/40 text-grey-400 border-transparent">
                        Upcoming
                    </Badge>
                )}
                {!workout.has_session && !isUpcoming && (
                    <Badge className="bg-warning-500/10 text-warning-400 border-transparent">
                        Missed
                    </Badge>
                )}
                <ChevronRight size={15} className="text-grey-600" />
            </div>
        </Button>
    )
}

// ─── Section ──────────────────────────────────────────────────────────────────

function Section({ title, workouts }: { title: string; workouts: WorkoutListItem[] }) {
    if (workouts.length === 0) return null
    return (
        <div>
            <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                {title}
            </p>
            <div className="flex flex-col gap-2">
                {workouts.map((w) => (
                    <WorkoutRow key={w.id} workout={w} />
                ))}
            </div>
        </div>
    )
}

// ─── Workout List ─────────────────────────────────────────────────────────────

export function WorkoutList() {
    const { data: programs } = useSuspenseQuery(programsQueryOptions({ status: 'IN_PROGRESS' }))

    const activeProgram = programs.results[0] ?? null
    const activePhase = activeProgram?.remaining_phases?.[0] ?? null

    const { data: workouts } = useSuspenseQuery(
        workoutsQueryOptions(activePhase ? { program_phase: activePhase.id } : undefined),
    )

    const today = new Date()
    today.setHours(0, 0, 0, 0)

    const upcoming = workouts.results
        .filter((w) => !w.has_session && w.planned_date && new Date(w.planned_date) >= today)
        .sort((a, b) => new Date(a.planned_date!).getTime() - new Date(b.planned_date!).getTime())

    const missed = workouts.results
        .filter((w) => !w.has_session && w.planned_date && new Date(w.planned_date) < today)
        .sort((a, b) => new Date(b.planned_date!).getTime() - new Date(a.planned_date!).getTime())

    const completed = workouts.results
        .filter((w) => w.has_session)
        .sort(
            (a, b) =>
                new Date(b.planned_date ?? '').getTime() - new Date(a.planned_date ?? '').getTime(),
        )

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
                <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400">
                    <Dumbbell size={18} />
                </div>
                <div>
                    <h1 className="text-2xl font-semibold text-grey-50">Workouts</h1>
                    {activeProgram && (
                        <p className="text-sm text-grey-400 mt-0.5">{activeProgram.program_name}</p>
                    )}
                </div>
            </div>

            {!activeProgram || !activePhase || workouts.count === 0 ? (
                <Empty className="border border-dashed border-grey-800">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <Dumbbell />
                        </EmptyMedia>
                        <EmptyTitle className="text-sm text-grey-300">No workouts yet</EmptyTitle>
                        <EmptyDescription className="text-xs">
                            Your trainer will assign workouts once your program is active.
                        </EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : (
                <div className="flex flex-col gap-8">
                    <Section title="Upcoming" workouts={upcoming} />
                    {upcoming.length > 0 && missed.length > 0 && (
                        <Separator className="bg-grey-800" />
                    )}
                    <Section title="Missed" workouts={missed} />
                    {(upcoming.length > 0 || missed.length > 0) && completed.length > 0 && (
                        <Separator className="bg-grey-800" />
                    )}
                    <Section title="Completed" workouts={completed} />
                </div>
            )}
        </div>
    )
}
