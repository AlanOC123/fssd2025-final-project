import { useState, useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Search, Plus, Trash2, Dumbbell } from 'lucide-react'
import { workoutsApi } from '@/features/workouts/api'
import type { WorkoutDetail, ExerciseRef } from '@/features/workouts/types'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import { useDebounce } from '@/shared/hooks/useDebounce'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
} from '@/shared/components/ui/sheet'
import { Badge } from '@/shared/components/ui/badge'
import { toast, toastApiError } from '@/shared/utils/toast'

// ─── Set Row ──────────────────────────────────────────────────────────────────

interface SetDraft {
    reps_prescribed: string
    weight_prescribed: string
}

function SetRow({
    index,
    set,
    onChange,
    onRemove,
    canRemove,
}: {
    index: number
    set: SetDraft
    onChange: (field: keyof SetDraft, val: string) => void
    onRemove: () => void
    canRemove: boolean
}) {
    return (
        <div className="flex items-center gap-2">
            <span className="text-xs text-grey-600 w-10 shrink-0">Set {index + 1}</span>
            <Input
                type="number"
                min={1}
                placeholder="Reps"
                value={set.reps_prescribed}
                onChange={(e) => onChange('reps_prescribed', e.target.value)}
                className="bg-grey-800 border-grey-700 text-grey-100 h-8 text-sm w-20"
            />
            <Input
                type="number"
                min={0}
                step={0.5}
                placeholder="kg"
                value={set.weight_prescribed}
                onChange={(e) => onChange('weight_prescribed', e.target.value)}
                className="bg-grey-800 border-grey-700 text-grey-100 h-8 text-sm w-20"
            />
            {canRemove && (
                <button
                    type="button"
                    onClick={onRemove}
                    className="text-grey-600 hover:text-danger-400 transition-colors"
                    aria-label="Remove set"
                >
                    <Trash2 size={13} />
                </button>
            )}
        </div>
    )
}

// ─── Selected Exercise Form ───────────────────────────────────────────────────

function ExerciseForm({
    exercise,
    workout,
    onDone,
    onCancel,
}: {
    exercise: ExerciseRef
    workout: WorkoutDetail
    onDone: () => void
    onCancel: () => void
}) {
    const queryClient = useQueryClient()
    const nextOrder = workout.exercises.length + 1

    const [trainerNotes, setTrainerNotes] = useState('')
    const [sets, setSets] = useState<SetDraft[]>([{ reps_prescribed: '', weight_prescribed: '' }])

    const addExerciseMutation = useMutation({
        mutationFn: workoutsApi.addExercise,
        onError: (err) => toastApiError(err, 'Failed to add exercise'),
    })

    const addSetMutation = useMutation({
        mutationFn: workoutsApi.addSet,
        onError: (err) => toastApiError(err, 'Failed to add set'),
    })

    const handleSave = async () => {
        const validSets = sets.filter((s) => s.reps_prescribed && Number(s.reps_prescribed) > 0)
        if (validSets.length === 0) {
            toast.error('Add at least one set with reps')
            return
        }

        try {
            await addExerciseMutation.mutateAsync({
                workout_id: workout.id,
                exercise_id: exercise.id,
                order: nextOrder,
                sets_prescribed: validSets.length,
                trainer_notes: trainerNotes,
            })

            // The response from addExercise is WorkoutDetail — we need the new exercise id
            // Re-fetch to get the created exercise id
            const updatedWorkout = await workoutsApi.get(workout.id)
            const createdExercise = updatedWorkout.exercises.find(
                (e) => e.exercise.id === exercise.id && e.order === nextOrder,
            )

            if (createdExercise) {
                await Promise.all(
                    validSets.map((s, i) =>
                        addSetMutation.mutateAsync({
                            workout_exercise_id: createdExercise.id,
                            set_order: i + 1,
                            reps_prescribed: Number(s.reps_prescribed),
                            weight_prescribed: Number(s.weight_prescribed) || 0,
                        }),
                    ),
                )
            }

            queryClient.invalidateQueries({ queryKey: ['workouts', workout.id] })
            toast.success(`${exercise.exercise_name} added`)
            onDone()
        } catch {
            // errors handled by mutation onError
        }
    }

    const isSaving = addExerciseMutation.isPending || addSetMutation.isPending

    return (
        <div className="flex flex-col gap-4 pt-4 px-4">
            {/* Exercise Header */}
            <div className="flex items-center gap-3 px-3 py-2 bg-grey-800 rounded-lg">
                <div className="flex items-center justify-center w-7 h-7 rounded-md bg-brand-500/10 text-brand-400 shrink-0">
                    <Dumbbell size={13} />
                </div>
                <div className="min-w-0">
                    <p className="text-sm font-medium text-grey-100 truncate">
                        {exercise.exercise_name}
                    </p>
                    {exercise.equipment.length > 0 && (
                        <p className="text-xs text-grey-500">
                            {exercise.equipment.map((e) => e.label).join(', ')}
                        </p>
                    )}
                </div>
            </div>

            {/* Sets */}
            <div>
                <div className="flex items-center gap-2 mb-2">
                    <Label className="text-grey-400 text-xs">Sets</Label>
                    <span className="text-grey-600 text-xs ml-auto">Reps · Weight (kg)</span>
                </div>
                <div className="flex flex-col gap-2">
                    {sets.map((set, i) => (
                        <SetRow
                            key={i}
                            index={i}
                            set={set}
                            onChange={(field, val) => {
                                const next = [...sets]
                                next[i] = { ...next[i], [field]: val }
                                setSets(next)
                            }}
                            onRemove={() => setSets(sets.filter((_, idx) => idx !== i))}
                            canRemove={sets.length > 1}
                        />
                    ))}
                </div>
                <button
                    type="button"
                    onClick={() =>
                        setSets([...sets, { reps_prescribed: '', weight_prescribed: '' }])
                    }
                    className="mt-2 text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1"
                >
                    <Plus size={12} />
                    Add set
                </button>
            </div>

            {/* Trainer Notes */}
            <div>
                <Label className="text-grey-400 text-xs mb-1.5 block">
                    Trainer Notes <span className="text-grey-600">(optional)</span>
                </Label>
                <Input
                    value={trainerNotes}
                    onChange={(e) => setTrainerNotes(e.target.value)}
                    placeholder="Cues, tempo, rest periods…"
                    className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600 h-8 text-sm"
                />
            </div>

            {/* Actions */}
            <div className="flex gap-2 pt-2">
                <Button size="sm" onClick={handleSave} disabled={isSaving} className="flex-1">
                    {isSaving ? 'Saving…' : 'Add to Workout'}
                </Button>
                <Button size="sm" variant="ghost" onClick={onCancel} className="text-grey-400">
                    Back
                </Button>
            </div>
        </div>
    )
}

// ─── Add Exercise Sheet ────────────────────────────────────────────────────────

interface AddExerciseSheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    workout: WorkoutDetail
}

export function AddExerciseSheet({ open, onOpenChange, workout }: AddExerciseSheetProps) {
    const [search, setSearch] = useState('')
    const [selected, setSelected] = useState<ExerciseRef | null>(null)
    const debouncedSearch = useDebounce(search, 300)

    const { data, isLoading } = useQuery({
        queryKey: ['exercises', debouncedSearch],
        queryFn: () =>
            api.get<PaginatedResponse<ExerciseRef>>('/exercises/exercises/', {
                params: { search: debouncedSearch, ordering: 'exercise_name' },
            }),
        enabled: open,
    })

    const exercises = data?.results ?? []

    // Reset on close
    useEffect(() => {
        if (!open) {
            setSearch('')
            setSelected(null)
        }
    }, [open])

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="bg-grey-900 border-grey-800 text-grey-50 w-full sm:max-w-md flex flex-col">
                <SheetHeader className="pb-4 border-b border-grey-800">
                    <SheetTitle className="text-grey-50">Add Exercise</SheetTitle>
                    <SheetDescription className="text-grey-400">
                        {selected ? 'Configure sets and reps' : 'Search and select an exercise'}
                    </SheetDescription>
                </SheetHeader>

                <div className="flex flex-col flex-1 overflow-hidden pt-4">
                    {selected ? (
                        <ExerciseForm
                            exercise={selected}
                            workout={workout}
                            onDone={() => onOpenChange(false)}
                            onCancel={() => setSelected(null)}
                        />
                    ) : (
                        <>
                            {/* Search */}
                            <div className="relative mb-3">
                                <Search
                                    size={14}
                                    className="absolute left-3 top-1/2 -translate-y-1/2 text-grey-500"
                                />
                                <Input
                                    value={search}
                                    onChange={(e) => setSearch(e.target.value)}
                                    placeholder="Search exercises…"
                                    className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600 pl-9"
                                    autoFocus
                                />
                            </div>

                            {/* Results */}
                            <div className="flex-1 overflow-y-auto flex flex-col gap-1">
                                {isLoading ? (
                                    <div className="flex items-center justify-center py-8">
                                        <div className="size-5 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
                                    </div>
                                ) : exercises.length === 0 ? (
                                    <p className="text-sm text-grey-600 text-center py-8">
                                        {search ? 'No exercises found' : 'Start typing to search'}
                                    </p>
                                ) : (
                                    exercises.map((ex) => (
                                        <button
                                            key={ex.id}
                                            type="button"
                                            onClick={() => setSelected(ex)}
                                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-grey-800 transition-colors text-left w-full group"
                                        >
                                            <div className="flex items-center justify-center w-7 h-7 rounded-md bg-grey-800 group-hover:bg-grey-700 text-grey-500 shrink-0">
                                                <Dumbbell size={13} />
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-grey-200 truncate">
                                                    {ex.exercise_name}
                                                </p>
                                                {ex.equipment.length > 0 && (
                                                    <p className="text-xs text-grey-600 truncate">
                                                        {ex.equipment
                                                            .map((e) => e.label)
                                                            .join(', ')}
                                                    </p>
                                                )}
                                            </div>
                                            <Badge className="bg-grey-800 group-hover:bg-grey-700 text-grey-500 border-transparent text-xs shrink-0">
                                                {ex.experience_level.label}
                                            </Badge>
                                        </button>
                                    ))
                                )}
                            </div>
                        </>
                    )}
                </div>
            </SheetContent>
        </Sheet>
    )
}
