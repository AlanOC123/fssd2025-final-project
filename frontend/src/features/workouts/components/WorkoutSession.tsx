import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useSuspenseQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle, SkipForward, ChevronRight, Dumbbell, Trophy } from 'lucide-react'
import { workoutDetailQueryOptions } from '@/features/workouts/api'
import { useSessionStore } from '@/features/workouts/db/sessionStore'
import { syncSession, SyncError } from '@/features/workouts/db/sync'
import type { WorkoutExercise, WorkoutSet } from '@/features/workouts/types'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Badge } from '@/shared/components/ui/badge'
import { Separator } from '@/shared/components/ui/separator'
import { toast } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'

// ─── Set Row ─────────────────────────────────────────────────────────────────

interface SetRowProps {
    set: WorkoutSet
    index: number
    isLogged: boolean
    isSkipped: boolean
    onLog: (reps: number, weight: number) => void
    onSkip: () => void
}

function SetRow({ set, index, isLogged, isSkipped, onLog, onSkip }: SetRowProps) {
    const [reps, setReps] = useState(String(set.reps_prescribed))
    const [weight, setWeight] = useState(String(set.weight_prescribed ?? ''))
    const done = isLogged || isSkipped

    return (
        <div
            className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-lg border transition-all',
                done
                    ? 'bg-grey-900/40 border-grey-800/50 opacity-60'
                    : 'bg-grey-900 border-grey-800',
            )}
        >
            <span className="text-xs text-grey-600 w-10 shrink-0">Set {index + 1}</span>

            <div className="flex items-center gap-2 flex-1">
                <Input
                    type="number"
                    value={reps}
                    onChange={(e) => setReps(e.target.value)}
                    disabled={done}
                    className="h-8 w-16 text-center text-sm"
                    placeholder="Reps"
                />
                <span className="text-grey-600 text-xs">×</span>
                <Input
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    disabled={done}
                    className="h-8 w-20 text-center text-sm"
                    placeholder="kg"
                />
            </div>

            {isLogged && <CheckCircle size={16} className="text-success-400 shrink-0" />}
            {isSkipped && <SkipForward size={16} className="text-grey-500 shrink-0" />}

            {!done && (
                <div className="flex items-center gap-1 shrink-0">
                    <Button
                        size="icon-sm"
                        variant="ghost"
                        onClick={() => onSkip()}
                        className="text-grey-500 hover:text-grey-300"
                        aria-label="Skip set"
                    >
                        <SkipForward size={14} />
                    </Button>
                    <Button
                        size="icon-sm"
                        onClick={() => onLog(Number(reps), Number(weight))}
                        disabled={!reps}
                        aria-label="Log set"
                    >
                        <CheckCircle size={14} />
                    </Button>
                </div>
            )}
        </div>
    )
}

// ─── Exercise Block ───────────────────────────────────────────────────────────

interface ExerciseBlockProps {
    exercise: WorkoutExercise
    isActive: boolean
    isComplete: boolean
    onStart: () => void
    onSkip: () => void
    onSetLog: (setId: string, reps: number, weight: number) => void
    onSetSkip: (setId: string) => void
    loggedSets: Set<string>
    skippedSets: Set<string>
}

function ExerciseBlock({
    exercise,
    isActive,
    isComplete,
    onStart,
    onSkip,
    onSetLog,
    onSetSkip,
    loggedSets,
    skippedSets,
}: ExerciseBlockProps) {
    const allSetsDone = exercise.sets.every((s) => loggedSets.has(s.id) || skippedSets.has(s.id))

    return (
        <div
            className={cn(
                'rounded-xl border overflow-hidden transition-all',
                isComplete
                    ? 'bg-grey-900/40 border-grey-800/50'
                    : isActive
                      ? 'bg-grey-900 border-brand-500/30 shadow-brand'
                      : 'bg-grey-900 border-grey-800 opacity-60',
            )}
        >
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-3">
                <div
                    className={cn(
                        'flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium shrink-0',
                        isComplete
                            ? 'bg-success-500/15 text-success-400'
                            : 'bg-grey-800 text-grey-500',
                    )}
                >
                    {isComplete ? <CheckCircle size={12} /> : exercise.order}
                </div>
                <p className="flex-1 text-sm font-medium text-grey-100 truncate">
                    {exercise.exercise.exercise_name}
                </p>
                <Badge className="bg-grey-800 text-grey-400 border-transparent shrink-0">
                    {exercise.sets_prescribed} sets
                </Badge>
            </div>

            {/* Actions when not yet started */}
            {!isActive && !isComplete && (
                <div className="px-4 pb-3 flex gap-2">
                    <Button size="sm" onClick={onStart} className="gap-1.5">
                        <Dumbbell size={13} />
                        Start
                    </Button>
                    <Button
                        size="sm"
                        variant="ghost"
                        onClick={onSkip}
                        className="text-grey-500 hover:text-grey-300 gap-1.5"
                    >
                        <SkipForward size={13} />
                        Skip
                    </Button>
                </div>
            )}

            {/* Sets when active */}
            {isActive && (
                <>
                    <Separator className="bg-grey-800" />
                    <div className="px-4 py-3 space-y-2">
                        {exercise.sets
                            .sort((a, b) => a.set_order - b.set_order)
                            .map((set, i) => (
                                <SetRow
                                    key={set.id}
                                    set={set}
                                    index={i}
                                    isLogged={loggedSets.has(set.id)}
                                    isSkipped={skippedSets.has(set.id)}
                                    onLog={(reps, weight) => onSetLog(set.id, reps, weight)}
                                    onSkip={() => onSetSkip(set.id)}
                                />
                            ))}
                    </div>
                    {allSetsDone && (
                        <div className="px-4 pb-3">
                            <p className="text-xs text-success-400 text-center">
                                All sets done — start the next exercise when ready
                            </p>
                        </div>
                    )}
                </>
            )}
        </div>
    )
}

// ─── Finished Screen ──────────────────────────────────────────────────────────

function FinishedScreen({ onSync, isSyncing }: { onSync: () => void; isSyncing: boolean }) {
    return (
        <div className="flex flex-col items-center justify-center min-h-[60vh] gap-6 p-6">
            <div className="flex items-center justify-center w-16 h-16 rounded-full bg-success-500/15">
                <Trophy size={28} className="text-success-400" />
            </div>
            <div className="text-center">
                <h2 className="text-xl font-semibold text-grey-50 mb-1">Workout complete!</h2>
                <p className="text-sm text-grey-400">Save your session to record your progress.</p>
            </div>
            <Button onClick={onSync} disabled={isSyncing} className="w-full max-w-xs">
                {isSyncing ? 'Saving...' : 'Save Session'}
            </Button>
        </div>
    )
}

// ─── Workout Session ─────────────────────────────────────────────────────────

export function WorkoutSession({ workoutId }: { workoutId: string }) {
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const { data: workout } = useSuspenseQuery(workoutDetailQueryOptions(workoutId))

    const {
        activeSession,
        activeExercise,
        startExercise,
        skipExercise,
        logSet,
        skipSet,
        finishSession,
        clearSession,
    } = useSessionStore()

    const [activeExerciseId, setActiveExerciseId] = useState<string | null>(
        activeExercise?.workoutExerciseId ?? null,
    )
    const [completedExerciseIds, setCompletedExerciseIds] = useState<Set<string>>(new Set())
    const [loggedSets, setLoggedSets] = useState<Set<string>>(new Set())
    const [skippedSets, setSkippedSets] = useState<Set<string>>(new Set())
    const [isFinished, setIsFinished] = useState(false)
    const [isSyncing, setIsSyncing] = useState(false)

    const exercises = workout.exercises.sort((a, b) => a.order - b.order)

    const handleStartExercise = async (workoutExerciseId: string) => {
        const { error } = await tryCatch(startExercise(workoutExerciseId))
        if (error) {
            toast.error('Failed to start exercise')
            return
        }
        setActiveExerciseId(workoutExerciseId)
    }

    const handleSkipExercise = async (workoutExerciseId: string) => {
        const { error } = await tryCatch(skipExercise(workoutExerciseId))
        if (error) {
            toast.error('Failed to skip exercise')
            return
        }
        setCompletedExerciseIds((prev) => new Set([...prev, workoutExerciseId]))
        setActiveExerciseId(null)
    }

    const handleLogSet = async (
        workoutSetId: string,
        repsCompleted: number,
        weightCompleted: number,
    ) => {
        const { error } = await tryCatch(logSet({ workoutSetId, repsCompleted, weightCompleted }))
        if (error) {
            toast.error('Failed to log set')
            return
        }
        setLoggedSets((prev) => new Set([...prev, workoutSetId]))
    }

    const handleSkipSet = async (workoutSetId: string) => {
        const { error } = await tryCatch(skipSet(workoutSetId))
        if (error) {
            toast.error('Failed to skip set')
            return
        }
        setSkippedSets((prev) => new Set([...prev, workoutSetId]))
    }

    const handleNextExercise = (currentExerciseId: string) => {
        setCompletedExerciseIds((prev) => new Set([...prev, currentExerciseId]))
        setActiveExerciseId(null)
    }

    const handleFinish = async () => {
        const { error } = await tryCatch(finishSession())
        if (error) {
            toast.error('Failed to finish session')
            return
        }
        setIsFinished(true)
    }

    const handleSync = async () => {
        if (!activeSession) return
        setIsSyncing(true)

        const { error } = await tryCatch(syncSession(activeSession))

        if (error) {
            setIsSyncing(false)
            const step = error instanceof SyncError ? error.step : 'unknown'
            toast.error('Sync failed', { description: `Failed at: ${step}. You can retry.` })
            return
        }

        queryClient.invalidateQueries({ queryKey: ['workouts'] })
        clearSession()
        toast.success('Session saved!')
        navigate({ to: ROUTES.client.dashboard })
    }

    const allExercisesDone = exercises.every((ex) => completedExerciseIds.has(ex.id))

    if (isFinished) {
        return <FinishedScreen onSync={handleSync} isSyncing={isSyncing} />
    }

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-6">
                <h1 className="text-lg font-semibold text-grey-50">{workout.workout_name}</h1>
                <Badge className="bg-grey-800 text-grey-400 border-transparent">
                    {completedExerciseIds.size}/{exercises.length}
                </Badge>
            </div>

            <div className="flex flex-col gap-3 mb-8">
                {exercises.map((exercise) => (
                    <ExerciseBlock
                        key={exercise.id}
                        exercise={exercise}
                        isActive={activeExerciseId === exercise.id}
                        isComplete={completedExerciseIds.has(exercise.id)}
                        onStart={() => handleStartExercise(exercise.id)}
                        onSkip={() => handleSkipExercise(exercise.id)}
                        onSetLog={(setId, reps, weight) => handleLogSet(setId, reps, weight)}
                        onSetSkip={(setId) => handleSkipSet(setId)}
                        loggedSets={loggedSets}
                        skippedSets={skippedSets}
                    />
                ))}
            </div>

            {activeExerciseId && (
                <Button
                    variant="outline"
                    className="w-full mb-3 gap-2"
                    onClick={() => handleNextExercise(activeExerciseId)}
                >
                    Next Exercise
                    <ChevronRight size={15} />
                </Button>
            )}

            {allExercisesDone && (
                <Button className="w-full gap-2" onClick={handleFinish}>
                    <Trophy size={16} />
                    Finish Workout
                </Button>
            )}
        </div>
    )
}
