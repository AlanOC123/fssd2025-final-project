import { useState } from 'react'
import { useSuspenseQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft, Plus, Trash2, Dumbbell, Calendar } from 'lucide-react'
import { workoutsApi, workoutDetailQueryOptions } from '@/features/workouts/api'
import type { WorkoutExercise } from '@/features/workouts/types'
import { AddExerciseSheet } from './AddExerciseSheet'
import { Button } from '@/shared/components/ui/button'
import { Badge } from '@/shared/components/ui/badge'
import { Separator } from '@/shared/components/ui/separator'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { toast, toastApiError } from '@/shared/utils/toast'
import { ROUTES } from '@/app/constants'

// ─── Set Table ────────────────────────────────────────────────────────────────

function SetTable({ exercise }: { exercise: WorkoutExercise }) {
    const queryClient = useQueryClient()

    const removeSetMutation = useMutation({
        mutationFn: workoutsApi.removeSet,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workouts', exercise.id] })
            // Invalidate parent workout too
        },
        onError: (err) => toastApiError(err, 'Failed to remove set'),
    })

    return (
        <div className="px-4 pb-3">
            <div className="flex items-center gap-2 mb-2 text-xs text-grey-600">
                <span className="w-10">Set</span>
                <span className="w-16">Reps</span>
                <span className="w-16">Weight</span>
            </div>
            <div className="flex flex-col gap-1.5">
                {exercise.sets.map((set) => (
                    <div key={set.id} className="flex items-center gap-2 text-sm">
                        <span className="text-grey-600 text-xs w-10">{set.set_order}</span>
                        <span className="text-grey-300 w-16">{set.reps_prescribed} reps</span>
                        <span className="text-grey-300 w-16">{set.weight_prescribed} kg</span>
                        <button
                            type="button"
                            onClick={() => removeSetMutation.mutate(set.id)}
                            disabled={removeSetMutation.isPending}
                            className="ml-auto text-grey-700 hover:text-danger-400 transition-colors"
                            aria-label="Remove set"
                        >
                            <Trash2 size={12} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    )
}

// ─── Exercise Card ────────────────────────────────────────────────────────────

function ExerciseCard({ exercise, workoutId }: { exercise: WorkoutExercise; workoutId: string }) {
    const queryClient = useQueryClient()

    const removeExerciseMutation = useMutation({
        mutationFn: () => workoutsApi.removeExercise(exercise.id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workouts', workoutId] })
            toast.success('Exercise removed')
        },
        onError: (err) => toastApiError(err, 'Failed to remove exercise'),
    })

    return (
        <div className="rounded-xl bg-grey-900 border border-grey-800 overflow-hidden">
            <div className="flex items-center gap-3 px-4 py-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-grey-800 text-grey-500 text-xs font-medium shrink-0">
                    {exercise.order}
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
                <div className="flex items-center gap-2 shrink-0">
                    <Badge className="bg-grey-800 text-grey-400 border-transparent">
                        {exercise.sets_prescribed} sets
                    </Badge>
                    <button
                        type="button"
                        onClick={() => removeExerciseMutation.mutate()}
                        disabled={removeExerciseMutation.isPending}
                        className="text-grey-600 hover:text-danger-400 transition-colors"
                        aria-label="Remove exercise"
                    >
                        <Trash2 size={14} />
                    </button>
                </div>
            </div>

            {exercise.sets.length > 0 && (
                <>
                    <Separator className="bg-grey-800" />
                    <SetTable exercise={exercise} />
                </>
            )}

            {exercise.trainer_notes && (
                <>
                    <Separator className="bg-grey-800" />
                    <p className="px-4 py-2 text-xs text-grey-500 italic">
                        {exercise.trainer_notes}
                    </p>
                </>
            )}
        </div>
    )
}

// ─── Trainer Workout Detail ───────────────────────────────────────────────────

export function TrainerWorkoutDetail({ workoutId }: { workoutId: string }) {
    const [addExerciseOpen, setAddExerciseOpen] = useState(false)
    const navigate = useNavigate()
    const queryClient = useQueryClient()
    const { data: workout } = useSuspenseQuery(workoutDetailQueryOptions(workoutId))

    const deleteWorkoutMutation = useMutation({
        mutationFn: () => workoutsApi.delete(workoutId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['workouts'] })
            toast.success('Workout deleted')
            navigate({ to: ROUTES.trainer.workouts })
        },
        onError: (err) => toastApiError(err, 'Failed to delete workout'),
    })

    const date = workout.planned_date
        ? new Date(workout.planned_date).toLocaleDateString('en-IE', {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
              year: 'numeric',
          })
        : null

    return (
        <>
            <div className="p-8 w-full">
                {/* Back */}
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate({ to: ROUTES.trainer.workouts })}
                    className="mb-6 -ml-2 text-grey-500 hover:text-grey-200"
                >
                    <ArrowLeft size={15} />
                    Workouts
                </Button>

                {/* Header */}
                <div className="flex items-start justify-between gap-4 mb-2">
                    <h1 className="text-2xl font-semibold text-grey-50">{workout.workout_name}</h1>
                    <button
                        type="button"
                        onClick={() => deleteWorkoutMutation.mutate()}
                        disabled={deleteWorkoutMutation.isPending}
                        className="text-grey-600 hover:text-danger-400 transition-colors mt-1"
                        aria-label="Delete workout"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>

                {date && (
                    <div className="flex items-center gap-1.5 text-xs text-grey-500 mb-8">
                        <Calendar size={12} />
                        <span>{date}</span>
                    </div>
                )}

                {!date && <div className="mb-8" />}

                <Separator className="bg-grey-800 mb-8" />

                {/* Exercises */}
                <div>
                    <div className="flex items-center justify-between mb-4">
                        <p className="text-xs font-medium text-grey-500 uppercase tracking-wider">
                            Exercises
                        </p>
                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() => setAddExerciseOpen(true)}
                            className="gap-1.5 h-7 text-xs border-grey-700 text-grey-300 hover:text-grey-50 hover:border-grey-600"
                        >
                            <Plus size={12} />
                            Add Exercise
                        </Button>
                    </div>

                    {workout.exercises.length === 0 ? (
                        <Empty className="border border-dashed border-grey-800 py-10">
                            <EmptyHeader>
                                <EmptyMedia variant="icon">
                                    <Dumbbell />
                                </EmptyMedia>
                                <EmptyTitle className="text-sm text-grey-500">
                                    No exercises yet
                                </EmptyTitle>
                                <EmptyDescription className="text-xs">
                                    Add exercises to build out this workout.
                                </EmptyDescription>
                            </EmptyHeader>
                            <Button
                                size="sm"
                                onClick={() => setAddExerciseOpen(true)}
                                className="gap-1.5"
                            >
                                <Plus size={13} />
                                Add First Exercise
                            </Button>
                        </Empty>
                    ) : (
                        <div className="flex flex-col gap-3">
                            {workout.exercises.map((ex) => (
                                <ExerciseCard key={ex.id} exercise={ex} workoutId={workout.id} />
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <AddExerciseSheet
                open={addExerciseOpen}
                onOpenChange={setAddExerciseOpen}
                workout={workout}
            />
        </>
    )
}
