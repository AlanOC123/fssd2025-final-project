import { useState } from 'react'
import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { Dumbbell, Calendar, ChevronRight, Plus, CheckCircle } from 'lucide-react'
import { workoutsQueryOptions } from '@/features/workouts/api'
import { programsQueryOptions } from '@/features/programs/api'
import type { WorkoutListItem } from '@/features/workouts/types'
import type { ProgramPhase } from '@/features/programs/types'
import { CreateWorkoutSheet } from './CreateWorkoutSheet'
import { Button } from '@/shared/components/ui/button'
import { Badge } from '@/shared/components/ui/badge'
import { Separator } from '@/shared/components/ui/separator'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/components/ui/select'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'

// ─── Status normaliser ────────────────────────────────────────────────────────
const PROGRAM_LABEL_TO_CODE: Record<string, string> = {
    Creating: 'CREATING',
    'Out for Review': 'OUT_FOR_REVIEW',
    'Ready to Begin': 'READY_TO_BEGIN',
    'In Progress': 'IN_PROGRESS',
    Completed: 'COMPLETED',
    Abandoned: 'ABANDONED',
}

function getProgramStatusCode(status: { code?: string; label: string }): string {
    return status.code ?? PROGRAM_LABEL_TO_CODE[status.label] ?? 'CREATING'
}

// ─── Workout Row ──────────────────────────────────────────────────────────────

function WorkoutRow({ workout }: { workout: WorkoutListItem }) {
    const navigate = useNavigate()

    const date = workout.planned_date
        ? new Date(workout.planned_date).toLocaleDateString('en-IE', {
              weekday: 'short',
              day: 'numeric',
              month: 'short',
          })
        : 'No date'

    return (
        <Button
            variant="outline"
            onClick={() => navigate({ to: `${ROUTES.trainer.workouts}/${workout.id}` })}
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
                <p className="text-sm font-medium text-grey-100 truncate">{workout.workout_name}</p>
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
                <ChevronRight size={15} className="text-grey-600" />
            </div>
        </Button>
    )
}

// ─── Trainer Workout List ─────────────────────────────────────────────────────

export function TrainerWorkoutList() {
    const [createOpen, setCreateOpen] = useState(false)
    const [selectedPhaseId, setSelectedPhaseId] = useState<string>('')

    // Get all live programs to populate the phase selector
    const { data: programs } = useSuspenseQuery(programsQueryOptions())

    // Flatten all phases from live programs into a single list for the selector
    const allPhases: (ProgramPhase & { programName: string })[] = programs.results
        .filter((p) =>
            ['CREATING', 'OUT_FOR_REVIEW', 'READY_TO_BEGIN', 'IN_PROGRESS'].includes(
                getProgramStatusCode(p.status),
            ),
        )
        .flatMap((p) =>
            p.remaining_phases.map((phase) => ({
                ...phase,
                programName: p.program_name,
            })),
        )

    const activePhaseId = selectedPhaseId || allPhases[0]?.id || ''
    const activePhase = allPhases.find((p) => p.id === activePhaseId) ?? allPhases[0]

    const { data: workouts } = useSuspenseQuery(
        workoutsQueryOptions(activePhaseId ? { program_phase: activePhaseId } : undefined),
    )

    const done = workouts.results.filter((w) => w.has_session)
    const pending = workouts.results.filter((w) => !w.has_session)

    return (
        <>
            <div className="p-8 w-full h-full">
                {/* Header */}
                <div className="flex items-center justify-between gap-4 mb-6">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400">
                            <Dumbbell size={18} />
                        </div>
                        <h1 className="text-2xl font-semibold text-grey-50">Workouts</h1>
                    </div>
                    {activePhase && (
                        <Button
                            size="sm"
                            onClick={() => setCreateOpen(true)}
                            className="gap-1.5 shrink-0"
                        >
                            <Plus size={13} />
                            New Workout
                        </Button>
                    )}
                </div>

                {/* Phase selector */}
                {allPhases.length > 1 && (
                    <div className="mb-6">
                        <Select value={activePhaseId} onValueChange={setSelectedPhaseId}>
                            <SelectTrigger className="bg-grey-900 border-grey-800 text-grey-200 w-full max-w-sm">
                                <SelectValue placeholder="Select a phase…" />
                            </SelectTrigger>
                            <SelectContent className="bg-grey-800 border-grey-700">
                                {allPhases.map((phase) => (
                                    <SelectItem
                                        key={phase.id}
                                        value={phase.id}
                                        className="text-grey-100 focus:bg-grey-700"
                                    >
                                        {phase.programName} —{' '}
                                        {phase.phase_name || phase.phase_option.label}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                )}

                {/* Active phase label */}
                {activePhase && allPhases.length === 1 && (
                    <p className="text-sm text-grey-400 mb-6">
                        {activePhase.programName} —{' '}
                        {activePhase.phase_name || activePhase.phase_option.label}
                    </p>
                )}

                {/* Empty state */}
                {!activePhase ? (
                    <Empty className="border border-dashed border-grey-800">
                        <EmptyHeader>
                            <EmptyMedia variant="icon">
                                <Dumbbell />
                            </EmptyMedia>
                            <EmptyTitle className="text-sm text-grey-300">
                                No active phases
                            </EmptyTitle>
                            <EmptyDescription className="text-xs">
                                Create a program and add phases before adding workouts.
                            </EmptyDescription>
                        </EmptyHeader>
                    </Empty>
                ) : workouts.count === 0 ? (
                    <Empty className="border border-dashed border-grey-800">
                        <EmptyHeader>
                            <EmptyMedia variant="icon">
                                <Dumbbell />
                            </EmptyMedia>
                            <EmptyTitle className="text-sm text-grey-300">
                                No workouts yet
                            </EmptyTitle>
                            <EmptyDescription className="text-xs">
                                Add workouts to this phase to get started.
                            </EmptyDescription>
                        </EmptyHeader>
                        <Button size="sm" onClick={() => setCreateOpen(true)} className="gap-1.5">
                            <Plus size={13} />
                            New Workout
                        </Button>
                    </Empty>
                ) : (
                    <div className="flex flex-col gap-8">
                        {pending.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                                    Scheduled
                                </p>
                                <div className="flex flex-col gap-2">
                                    {pending.map((w) => (
                                        <WorkoutRow key={w.id} workout={w} />
                                    ))}
                                </div>
                            </div>
                        )}
                        {pending.length > 0 && done.length > 0 && (
                            <Separator className="bg-grey-800" />
                        )}
                        {done.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                                    Completed
                                </p>
                                <div className="flex flex-col gap-2">
                                    {done.map((w) => (
                                        <WorkoutRow key={w.id} workout={w} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {activePhase && (
                <CreateWorkoutSheet
                    open={createOpen}
                    onOpenChange={setCreateOpen}
                    phase={activePhase}
                />
            )}
        </>
    )
}
