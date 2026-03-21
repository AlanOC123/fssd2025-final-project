import { useForm } from '@tanstack/react-form'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'
import { programsApi, PROGRAM_QUERY_KEY } from '@/features/programs/api'
import { membershipsApi } from '@/features/memberships/api'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import type { LabelLookup } from '@/shared/types/base'
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
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/components/ui/select'
import { toast, toastApiError } from '@/shared/utils/toast'
import { useNavigate } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'

// ─── Schema ───────────────────────────────────────────────────────────────────

const createProgramSchema = z.object({
    program_name: z.string().min(1, 'Program name is required').max(150, 'Max 150 characters'),
    trainer_client_membership_id: z.string().min(1, 'Please select a client'),
    training_goal_id: z.string().min(1, 'Please select a training goal'),
    experience_level_id: z.string().min(1, 'Please select an experience level'),
})

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

// ─── Create Program Sheet ─────────────────────────────────────────────────────

interface CreateProgramSheetProps {
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function CreateProgramSheet({ open, onOpenChange }: CreateProgramSheetProps) {
    const queryClient = useQueryClient()
    const navigate = useNavigate()

    // Fetch active memberships to populate client selector
    const { data: membershipsData, isLoading: loadingMemberships } = useQuery({
        queryKey: ['memberships', { status: 'Active' }],
        queryFn: () => membershipsApi.list({ status: 'Active' }),
        enabled: open,
    })

    // Fetch training goals (public endpoint)
    const { data: goalsData, isLoading: loadingGoals } = useQuery({
        queryKey: ['training-goals'],
        queryFn: () => api.get<PaginatedResponse<LabelLookup>>('/users/training-goals/'),
        enabled: open,
    })

    // Fetch experience levels (public endpoint)
    const { data: levelsData, isLoading: loadingLevels } = useQuery({
        queryKey: ['experience-levels'],
        queryFn: () => api.get<PaginatedResponse<LabelLookup>>('/users/experience-levels/'),
        enabled: open,
    })

    const memberships = membershipsData?.results ?? []
    const goals = goalsData?.results ?? []
    const levels = levelsData?.results ?? []

    const createMutation = useMutation({
        mutationFn: programsApi.create,
        onSuccess: (program) => {
            toast.success('Program created', {
                description: `"${program.program_name}" is ready to build out.`,
            })
            queryClient.invalidateQueries({ queryKey: PROGRAM_QUERY_KEY() })
            onOpenChange(false)
            navigate({ to: `${ROUTES.trainer.programs}/${program.id}` })
        },
        onError: (error) => toastApiError(error, 'Failed to create program'),
    })

    const form = useForm({
        defaultValues: {
            program_name: '',
            trainer_client_membership_id: '',
            training_goal_id: '',
            experience_level_id: '',
        },
        validators: {
            onSubmit: createProgramSchema,
        },
        onSubmit: async ({ value }) => {
            await createMutation.mutateAsync(value)
        },
    })

    const isLoading = loadingMemberships || loadingGoals || loadingLevels

    return (
        <Sheet open={open} onOpenChange={onOpenChange}>
            <SheetContent className="bg-grey-900 border-grey-800 text-grey-50 w-full sm:max-w-md flex flex-col">
                <SheetHeader className="pb-6 border-b border-grey-800">
                    <SheetTitle className="text-grey-50">New Program</SheetTitle>
                    <SheetDescription className="text-grey-400">
                        Create a training program for one of your active clients.
                    </SheetDescription>
                </SheetHeader>

                {isLoading ? (
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
                        {/* Program Name */}
                        <form.Field name="program_name">
                            {(field) => (
                                <div>
                                    <Label
                                        htmlFor="program_name"
                                        className="text-grey-300 mb-1.5 block"
                                    >
                                        Program Name
                                    </Label>
                                    <Input
                                        id="program_name"
                                        placeholder="e.g. 12-Week Hypertrophy Block"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        className="bg-grey-800 border-grey-700 text-grey-100 placeholder:text-grey-600"
                                        aria-invalid={field.state.meta.errors.length > 0}
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Client (Membership) */}
                        <form.Field name="trainer_client_membership_id">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">Client</Label>
                                    {memberships.length === 0 ? (
                                        <p className="text-sm text-grey-500 bg-grey-800 border border-grey-700 rounded-md px-3 py-2">
                                            No active clients — accept a membership request first.
                                        </p>
                                    ) : (
                                        <Select
                                            value={field.state.value}
                                            onValueChange={field.handleChange}
                                        >
                                            <SelectTrigger className="bg-grey-800 border-grey-700 text-grey-100 w-full">
                                                <SelectValue placeholder="Select a client…" />
                                            </SelectTrigger>
                                            <SelectContent className="bg-grey-800 border-grey-700">
                                                {memberships.map((m) => (
                                                    <SelectItem
                                                        key={m.id}
                                                        value={m.id}
                                                        className="text-grey-100 focus:bg-grey-700 focus:text-grey-50"
                                                    >
                                                        {m.client_name}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    )}
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Training Goal */}
                        <form.Field name="training_goal_id">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Training Goal
                                    </Label>
                                    <Select
                                        value={field.state.value}
                                        onValueChange={field.handleChange}
                                    >
                                        <SelectTrigger className="bg-grey-800 border-grey-700 text-grey-100 w-full">
                                            <SelectValue placeholder="Select a goal…" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-grey-800 border-grey-700">
                                            {goals.map((g) => (
                                                <SelectItem
                                                    key={g.id}
                                                    value={g.id}
                                                    className="text-grey-100 focus:bg-grey-700 focus:text-grey-50"
                                                >
                                                    {g.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        {/* Experience Level */}
                        <form.Field name="experience_level_id">
                            {(field) => (
                                <div>
                                    <Label className="text-grey-300 mb-1.5 block">
                                        Experience Level
                                    </Label>
                                    <Select
                                        value={field.state.value}
                                        onValueChange={field.handleChange}
                                    >
                                        <SelectTrigger className="bg-grey-800 border-grey-700 text-grey-100 w-full">
                                            <SelectValue placeholder="Select a level…" />
                                        </SelectTrigger>
                                        <SelectContent className="bg-grey-800 border-grey-700">
                                            {levels.map((l) => (
                                                <SelectItem
                                                    key={l.id}
                                                    value={l.id}
                                                    className="text-grey-100 focus:bg-grey-700 focus:text-grey-50"
                                                >
                                                    {l.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
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
                                        disabled={
                                            isSubmitting ||
                                            createMutation.isPending ||
                                            memberships.length === 0
                                        }
                                    >
                                        {isSubmitting || createMutation.isPending
                                            ? 'Creating…'
                                            : 'Create Program'}
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
