import { useEffect } from 'react'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { workoutsApi, WORKOUT_QUERY_KEY } from '@/features/workouts/api'
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
import { toast, toastApiError } from '@/shared/utils/toast'
import { useNavigate } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import type { ProgramPhase } from '@/features/programs/types'

// ─── Schema ───────────────────────────────────────────────────────────────────

const schema = z.object({
    workout_name: z.string().min(1, 'Workout name is required').max(300, 'Max 300 characters'),
    planned_date: z.string().or(z.undefined()),
})

function FieldError({ errors }: { errors: unknown[] }) {
    if (!errors.length) return null
    const msg = errors[0]
    const text =
        msg && typeof msg === 'object' && 'message' in msg
            ? String((msg as { message: string }).message)
            : String(msg)
    return <p className="text-xs text-destructive mt-1">{text}</p>
}

// ─── Create Workout Sheet ─────────────────────────────────────────────────────

interface CreateWorkoutSheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    phase: ProgramPhase
}

export function CreateWorkoutSheet({ open, onOpenChange, phase }: CreateWorkoutSheetProps) {
    const queryClient = useQueryClient()
    const navigate = useNavigate()

    const mutation = useMutation({
        mutationFn: workoutsApi.create,
        onSuccess: (workout) => {
            toast.success('Workout created')
            queryClient.invalidateQueries({
                queryKey: WORKOUT_QUERY_KEY({ program_phase: phase.id }),
            })
            onOpenChange(false)
            navigate({ to: `${ROUTES.trainer.workouts}/${workout.id}` })
        },
        onError: (err) => toastApiError(err, 'Failed to create workout'),
    })

    const form = useForm({
        defaultValues: { workout_name: '', planned_date: undefined as string | undefined },
        validators: { onSubmit: schema },
        onSubmit: async ({ value }) => {
            await mutation.mutateAsync({
                program_phase_id: phase.id,
                workout_name: value.workout_name,
                planned_date: value.planned_date || null,
            })
        },
    })

    useEffect(() => {
        if (!open) form.reset()
    }, [open])

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="bg-grey-900 border-grey-800 text-grey-50 w-full sm:max-w-md flex flex-col px-4 pt-6">
                <SheetHeader className="pb-6 border-b border-grey-800">
                    <SheetTitle className="text-grey-50">New Workout</SheetTitle>
                    <SheetDescription className="text-grey-400">
                        Adding to{' '}
                        <span className="text-grey-300">
                            {phase.phase_name || phase.phase_option.label}
                        </span>
                    </SheetDescription>
                </SheetHeader>

                <form
                    onSubmit={(e) => {
                        e.preventDefault()
                        form.handleSubmit()
                    }}
                    className="flex flex-col flex-1 pt-6 gap-5"
                >
                    <form.Field name="workout_name">
                        {(field) => (
                            <div>
                                <Label className="text-grey-300 mb-1.5 block">Workout Name</Label>
                                <Input
                                    placeholder="e.g. Upper Body A"
                                    value={field.state.value}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    onBlur={field.handleBlur}
                                    className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600"
                                    autoFocus
                                />
                                <FieldError errors={field.state.meta.errors} />
                            </div>
                        )}
                    </form.Field>

                    <form.Field name="planned_date">
                        {(field) => (
                            <div>
                                <Label className="text-grey-300 mb-1.5 block">
                                    Planned Date{' '}
                                    <span className="text-grey-600 font-normal">(optional)</span>
                                </Label>
                                <Input
                                    type="date"
                                    value={field.state.value ?? ''}
                                    onChange={(e) =>
                                        field.handleChange(e.target.value || undefined)
                                    }
                                    onBlur={field.handleBlur}
                                    className="bg-grey-800 border-grey-700 text-grey-100"
                                />
                                <FieldError errors={field.state.meta.errors} />
                            </div>
                        )}
                    </form.Field>

                    <div className="mt-auto pt-4 border-t border-grey-800">
                        <form.Subscribe selector={(s) => s.isSubmitting}>
                            {(isSubmitting) => (
                                <Button
                                    type="submit"
                                    className="w-full"
                                    disabled={isSubmitting || mutation.isPending}
                                >
                                    {isSubmitting || mutation.isPending
                                        ? 'Creating…'
                                        : 'Create Workout'}
                                </Button>
                            )}
                        </form.Subscribe>
                    </div>
                </form>
            </SheetContent>
        </Sheet>
    )
}
