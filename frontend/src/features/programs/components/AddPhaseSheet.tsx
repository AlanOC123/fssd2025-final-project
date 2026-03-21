import { useEffect } from 'react'
import { useForm } from '@tanstack/react-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { format, addDays } from 'date-fns'
import { programsApi } from '@/features/programs/api'
import type { ProgramDetail } from '@/features/programs/types'
import type { PhaseOptionLookup, CreatePhasePayload } from '@/features/programs/types'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { Textarea } from '@/shared/components/ui/textarea'
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
    SheetDescription,
} from '@/shared/components/ui/sheet'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/components/ui/select'
import { toast, toastApiError } from '@/shared/utils/toast'

// ─── Schema ───────────────────────────────────────────────────────────────────

const addPhaseSchema = z
    .object({
        phase_option_id: z.string().min(1, 'Please select a phase type'),
        phase_name: z.string().max(120, 'Max 120 characters'),
        phase_goal: z.string().max(200, 'Max 200 characters'),
        planned_start_date: z.string().min(1, 'Start date is required'),
        planned_end_date: z.string().min(1, 'End date is required'),
        trainer_notes: z.string().max(500, 'Max 500 characters'),
        client_notes: z.string().max(500, 'Max 500 characters'),
    })
    .refine(
        (d) =>
            !d.planned_start_date ||
            !d.planned_end_date ||
            d.planned_end_date > d.planned_start_date,
        { message: 'End date must be after start date', path: ['planned_end_date'] },
    )

// ─── Field Error ─────────────────────────────────────────────────────────────

function FieldError({ errors }: { errors: unknown[] }) {
    if (!errors.length) return null
    const msg = errors[0]
    const text =
        msg && typeof msg === 'object' && 'message' in msg
            ? String((msg as { message: string }).message)
            : String(msg)
    return <p className="text-xs text-destructive mt-1">{text}</p>
}

// ─── Add Phase Sheet ──────────────────────────────────────────────────────────

interface AddPhaseSheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
    program: ProgramDetail
}

export function AddPhaseSheet({ open, onOpenChange, program }: AddPhaseSheetProps) {
    const queryClient = useQueryClient()

    const { data: optionsData, isLoading: loadingOptions } = useQuery({
        queryKey: ['program-phase-options'],
        queryFn: () =>
            api.get<PaginatedResponse<PhaseOptionLookup>>('/programs/program-phase-options/'),
        enabled: open,
    })

    const phaseOptions = optionsData?.results ?? []

    // Next sequence order = last phase + 1, or 1 if no phases yet
    const nextSequenceOrder =
        program.phases.length > 0 ? Math.max(...program.phases.map((p) => p.sequence_order)) + 1 : 1

    // Default start = day after last phase ends, or today
    const defaultStart =
        program.phases.length > 0
            ? (() => {
                  const lastEnd = program.phases
                      .map((p) => p.planned_end_date)
                      .filter(Boolean)
                      .sort()
                      .at(-1)
                  return lastEnd
                      ? format(addDays(new Date(lastEnd), 1), 'yyyy-MM-dd')
                      : format(new Date(), 'yyyy-MM-dd')
              })()
            : format(new Date(), 'yyyy-MM-dd')

    const createPhaseMutation = useMutation({
        mutationFn: (payload: CreatePhasePayload) => programsApi.createPhase(payload),
        onSuccess: () => {
            toast.success('Phase added')
            queryClient.invalidateQueries({ queryKey: ['programs', program.id] })
            onOpenChange(false)
        },
        onError: (error) => toastApiError(error, 'Failed to add phase'),
    })

    const form = useForm({
        defaultValues: {
            phase_option_id: '',
            phase_name: '',
            phase_goal: '',
            planned_start_date: defaultStart,
            planned_end_date: '',
            trainer_notes: '',
            client_notes: '',
        },
        validators: { onSubmit: addPhaseSchema },
        onSubmit: async ({ value }) => {
            await createPhaseMutation.mutateAsync({
                program_id: program.id,
                phase_option_id: value.phase_option_id,
                phase_name: value.phase_name,
                phase_goal: value.phase_goal,
                sequence_order: nextSequenceOrder,
                planned_start_date: value.planned_start_date,
                planned_end_date: value.planned_end_date,
                trainer_notes: value.trainer_notes,
                client_notes: value.client_notes,
            })
        },
    })

    // When a phase type is selected, auto-fill the end date based on its default duration
    function handlePhaseOptionChange(optionId: string, setField: (val: string) => void) {
        setField(optionId)
        const option = phaseOptions.find((o) => o.id === optionId)
        if (option && form.getFieldValue('planned_start_date')) {
            const start = new Date(form.getFieldValue('planned_start_date'))
            const end = addDays(start, option.default_duration_days - 1)
            form.setFieldValue('planned_end_date', format(end, 'yyyy-MM-dd'))
        }
    }

    // Reset form when sheet closes
    useEffect(() => {
        if (!open) {
            form.reset()
        }
    }, [open])

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="bg-grey-900 border-grey-800 text-grey-50 w-full sm:max-w-md flex flex-col overflow-y-auto">
                <SheetHeader className="pb-6 border-b border-grey-800">
                    <SheetTitle className="text-grey-50">Add Phase</SheetTitle>
                    <SheetDescription className="text-grey-400">
                        Phase {nextSequenceOrder} of{' '}
                        <span className="text-grey-300">{program.program_name}</span>
                    </SheetDescription>
                </SheetHeader>

                {loadingOptions ? (
                    <div className="flex-1 flex items-center justify-center">
                        <div className="size-5 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
                    </div>
                ) : (
                    <form
                        onSubmit={(e) => {
                            e.preventDefault()
                            form.handleSubmit()
                        }}
                        className="flex flex-col flex-1 pt-6 px-4 gap-5"
                    >
                        {/* Phase Type */}
                        <form.Field name="phase_option_id">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">Phase Type</Label>
                                    <Select
                                        value={field.state.value}
                                        onValueChange={(val) =>
                                            handlePhaseOptionChange(val, field.handleChange)
                                        }
                                    >
                                        <SelectTrigger className="bg-grey-800 border-grey-700 text-grey-100 w-full">
                                            <SelectValue placeholder="Select a phase type…" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-grey-800 border-grey-700">
                                            {phaseOptions.map((o) => (
                                                <SelectItem
                                                    key={o.id}
                                                    value={o.id}
                                                    className="text-grey-100 focus:bg-grey-700 focus:text-grey-50"
                                                >
                                                    <span>{o.label}</span>
                                                    <span className="ml-2 text-grey-500 text-xs">
                                                        ({o.default_duration_weeks}w default)
                                                    </span>
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Phase Name */}
                        <form.Field name="phase_name">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Phase Name{' '}
                                        <span className="text-grey-600 font-normal">
                                            (optional)
                                        </span>
                                    </Label>
                                    <Input
                                        placeholder="e.g. Foundation Block"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600"
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Phase Goal */}
                        <form.Field name="phase_goal">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Phase Goal{' '}
                                        <span className="text-grey-600 font-normal">
                                            (optional)
                                        </span>
                                    </Label>
                                    <Input
                                        placeholder="e.g. Build aerobic base and movement patterns"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600"
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Dates */}
                        <div className="grid grid-cols-2 gap-3">
                            <form.Field name="planned_start_date">
                                {(field) => (
                                    <div>
                                        <Label className="text-grey-300 mb-1.5 block">
                                            Start Date
                                        </Label>
                                        <div className="relative">
                                            <Input
                                                type="date"
                                                value={field.state.value}
                                                onChange={(e) => field.handleChange(e.target.value)}
                                                onBlur={field.handleBlur}
                                                className="bg-grey-800 border-grey-700 text-grey-100"
                                            />
                                        </div>
                                        <FieldError errors={field.state.meta.errors} />
                                    </div>
                                )}
                            </form.Field>

                            <form.Field name="planned_end_date">
                                {(field) => (
                                    <div>
                                        <Label className="text-grey-300 mb-1.5 block">
                                            End Date
                                        </Label>
                                        <Input
                                            type="date"
                                            value={field.state.value}
                                            onChange={(e) => field.handleChange(e.target.value)}
                                            onBlur={field.handleBlur}
                                            className="bg-grey-800 border-grey-700 text-grey-100"
                                        />
                                        <FieldError errors={field.state.meta.errors} />
                                    </div>
                                )}
                            </form.Field>
                        </div>

                        {/* Trainer Notes */}
                        <form.Field name="trainer_notes">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Trainer Notes{' '}
                                        <span className="text-grey-600 font-normal">
                                            (optional)
                                        </span>
                                    </Label>
                                    <Textarea
                                        placeholder="Internal notes for this phase…"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600 resize-none"
                                        rows={2}
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Client Notes */}
                        <form.Field name="client_notes">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Client Notes{' '}
                                        <span className="text-grey-600 font-normal">
                                            (optional)
                                        </span>
                                    </Label>
                                    <Textarea
                                        placeholder="Notes visible to the client…"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600 resize-none"
                                        rows={2}
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Submit */}
                        <div className="mt-auto pt-4 border-t border-grey-800">
                            <form.Subscribe selector={(s) => s.isSubmitting}>
                                {(isSubmitting) => (
                                    <Button
                                        type="submit"
                                        className="w-full"
                                        disabled={isSubmitting || createPhaseMutation.isPending}
                                    >
                                        {isSubmitting || createPhaseMutation.isPending
                                            ? 'Adding…'
                                            : 'Add Phase'}
                                    </Button>
                                )}
                            </form.Subscribe>
                        </div>
                    </form>
                )}
            </SheetContent>
        </Sheet>
    )
}
