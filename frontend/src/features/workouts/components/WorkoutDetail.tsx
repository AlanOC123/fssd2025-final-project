import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import {
    ArrowLeft,
    Dumbbell,
    PlayCircle,
    Calendar,
    Info,
    CheckCircle,
} from 'lucide-react'
import { workoutDetailQueryOptions } from '@/features/workouts/api'
import { useSessionStore } from '@/features/workouts/db/sessionStore'
import type { WorkoutExercise } from '@/features/workouts/types'
import { Button } from '@/shared/components/ui/button'
import { Badge } from '@/shared/components/ui/badge'
import { Separator } from '@/shared/components/ui/separator'
import { toast, toastApiError } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'
import { ROUTES } from '@/app/constants'

// ─── Exercise Card ────────────────────────────────────────────────────────────

function ExerciseCard({ exercise, index }: { exercise: WorkoutExercise; index: number }) {
    return (
        <div className="rounded-xl bg-grey-900 border border-grey-800 overflow-hidden">
            {/* Header */}
            <div className="flex items-center gap-3 px-4 py-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-grey-800 text-grey-500 text-xs font-medium shrink-0">
                    {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-grey-100 truncate">
                        {exercise.exercise.exercise_name}
                    </p>
                    {exercise.exercise.equipment.length > 0 && (
                        <p className="text-xs text-grey-500 mt-0.5">
                            {exercise.exercise.equipment.map((e) => e.label).join(', ')}
                        </p>
                    )}
                </div>
                <Badge className="bg-grey-800 text-grey-400 border-transparent shrink-0">
                    {exercise.sets_prescribed} sets
                </Badge>
            </div>

            <Separator className="bg-grey-800" />

            {/* Sets */}
            <div className="px-4 py-3 space-y-2">
                {exercise.sets.map((set) => (
                    <div key={set.id} className="flex items-center gap-4 text-sm">
                        <span className="text-grey-600 text-xs w-12">Set {set.set_order}</span>
                        <span className="text-grey-300">{set.reps_prescribed} reps</span>
                        {set.weight_prescribed != null && (
                            <>
                                <span className="text-grey-700">·</span>
                                <span className="text-grey-300">{set.weight_prescribed} kg</span>
                            </>
                        )}
                    </div>
                ))}
            </div>

            {/* Trainer notes */}
            {exercise.trainer_notes && (
                <>
                    <Separator className="bg-grey-800" />
                    <div className="flex items-start gap-2 px-4 py-3">
                        <Info size={13} className="text-grey-500 mt-0.5 shrink-0" />
                        <p className="text-xs text-grey-400">{exercise.trainer_notes}</p>
                    </div>
                </>
            )}
        </div>
    )
}

// ─── Workout Detail ───────────────────────────────────────────────────────────

export function WorkoutDetail({ workoutId }: { workoutId: string }) {
    const navigate = useNavigate()
    const { data: workout } = useSuspenseQuery(workoutDetailQueryOptions(workoutId))
    const { startSession, loadSession } = useSessionStore()

    const date = workout.planned_date
        ? new Date(workout.planned_date).toLocaleDateString('en-IE', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
          })
        : null

    const handleStart = async () => {
        // Check for an existing unfinished local session first
        const { data: existing } = await tryCatch(loadSession(workoutId))

        if (existing) {
            // Resume existing session
            navigate({ to: `${ROUTES.client.workouts}/${workoutId}/session` })
            return
        }

        const { error } = await tryCatch(startSession(workoutId))

        if (error) {
            toastApiError(error, 'Could not start workout')
            return
        }

        toast.success('Workout started!')
        navigate({ to: `${ROUTES.client.workouts}/${workoutId}/session` })
    }

    return (
        <div className="p-6 max-w-2xl mx-auto">
            {/* Back */}
            <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate({ to: ROUTES.client.dashboard })}
                className="mb-6 -ml-2 text-grey-500 hover:text-grey-200"
            >
                <ArrowLeft size={15} />
                Dashboard
            </Button>

            {/* Header */}
            <div className="mb-6">
                <div className="flex items-start justify-between gap-4 mb-2">
                    <h1 className="text-2xl font-semibold text-grey-50">{workout.workout_name}</h1>
                </div>

                {date && (
                    <div className="flex items-center gap-1.5 text-xs text-grey-500">
                        <Calendar size={12} />
                        <span>{date}</span>
                    </div>
                )}

                <div className="flex items-center gap-3 mt-3 text-xs text-grey-500">
                    <span>{workout.exercises.length} exercises</span>
                    <span className="text-grey-700">·</span>
                    <span>
                        {workout.exercises.reduce((acc, ex) => acc + ex.sets_prescribed, 0)} sets
                        total
                    </span>
                </div>
            </div>

            {/* Start button */}
            {workout.has_session ? (
                <div className="w-full mb-8 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-success-500/10 border border-success-500/20">
                    <CheckCircle size={16} className="text-success-400" />
                    <span className="text-sm text-success-400 font-medium">
                        Session already completed
                    </span>
                </div>
            ) : (
                <Button className="w-full mb-8 gap-2" onClick={handleStart}>
                    <PlayCircle size={18} />
                    Start Workout
                </Button>
            )}

            <Separator className="bg-grey-800 mb-8" />

            {/* Exercises */}
            <div>
                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-4">
                    Exercises
                </p>
                {workout.exercises.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-10 gap-2 rounded-lg border border-dashed border-grey-800">
                        <Dumbbell size={20} className="text-grey-600" />
                        <p className="text-sm text-grey-500">No exercises added yet</p>
                    </div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {workout.exercises
                            .sort((a, b) => a.order - b.order)
                            .map((exercise, i) => (
                                <ExerciseCard key={exercise.id} exercise={exercise} index={i} />
                            ))}
                    </div>
                )}
            </div>
        </div>
    )
}
