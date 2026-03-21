import { useState } from 'react'
import { useForm } from '@tanstack/react-form'
import { useNavigate } from '@tanstack/react-router'
import { z } from 'zod'
import { Users, Dumbbell, ArrowLeft } from 'lucide-react'
import { authApi } from '@/features/auth/api'
import { useAuthStore } from '@/features/auth/store'
import { ROUTES } from '@/app/constants'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { toast, toastApiError } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'
import { router } from '@/app/router'
import { cn } from '@/shared/utils/utils'

type Role = 'trainer' | 'client'

// ─── Schema ───────────────────────────────────────────────────────────────────

const registerSchema = z
    .object({
        first_name: z.string().min(1, 'First name is required'),
        last_name: z.string().min(1, 'Last name is required'),
        email: z.email('Please enter a valid email'),
        password1: z.string().min(8, 'Password must be at least 8 characters'),
        password2: z.string().min(1, 'Please confirm your password'),
    })
    .refine((d) => d.password1 === d.password2, {
        message: 'Passwords do not match',
        path: ['password2'],
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

// ─── Role Card ────────────────────────────────────────────────────────────────

function RoleCard({
    role,
    selected,
    onClick,
}: {
    role: Role
    selected: boolean
    onClick: () => void
}) {
    const isTrainer = role === 'trainer'

    return (
        <button
            type="button"
            onClick={onClick}
            className={cn(
                'relative flex flex-col items-center gap-4 rounded-xl border-2 p-6 text-center transition-all duration-200 cursor-pointer w-full',
                selected
                    ? 'border-brand-500 bg-brand-500/10'
                    : 'border-grey-700 bg-grey-900 hover:border-grey-600 hover:bg-grey-800',
            )}
        >
            <div
                className={cn(
                    'flex items-center justify-center w-12 h-12 rounded-xl',
                    selected ? 'bg-brand-500/20 text-brand-400' : 'bg-grey-800 text-grey-400',
                )}
            >
                {isTrainer ? <Dumbbell size={22} /> : <Users size={22} />}
            </div>
            <div>
                <p
                    className={cn(
                        'text-sm font-semibold',
                        selected ? 'text-brand-300' : 'text-grey-100',
                    )}
                >
                    {isTrainer ? 'I am a Trainer' : 'I am a Client'}
                </p>
                <p className="text-xs text-grey-500 mt-1">
                    {isTrainer
                        ? 'Create programs and manage clients'
                        : 'Follow programs and track progress'}
                </p>
            </div>
            {selected && (
                <span className="absolute top-3 right-3 w-2 h-2 rounded-full bg-brand-400" />
            )}
        </button>
    )
}

// ─── Register Page ────────────────────────────────────────────────────────────

export function RegisterPage() {
    const [role, setRole] = useState<Role | null>(null)
    const navigate = useNavigate()

    const login = useAuthStore((s) => s.login)

    const form = useForm({
        defaultValues: {
            first_name: '',
            last_name: '',
            email: '',
            password1: '',
            password2: '',
        },
        validators: { onSubmit: registerSchema },
        onSubmit: async ({ value }) => {
            if (!role) return

            // Step 1: Register the account
            const { error: registerError } = await tryCatch(authApi.register({ ...value, role }))

            if (registerError) {
                toastApiError(registerError, 'Registration failed')
                return
            }

            // Step 2: Log in using the same credentials — this sets the JWT
            // cookies through the exact same proven flow as LoginPage.
            // Registration returns tokens but we can't rely on those cookies
            // being committed before subsequent requests fire.
            const { error: loginError } = await tryCatch(
                login({ email: value.email, password: value.password1 }),
            )

            if (loginError) {
                toastApiError(loginError, 'Login after registration failed')
                return
            }

            const user = useAuthStore.getState().user!

            toast.success('Account created', {
                description: `Welcome to Apex, ${user.first_name}!`,
            })

            await navigate({
                to: user.is_client ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })

            router.invalidate()
        },
    })

    return (
        <div className="min-h-dvh flex items-center justify-center bg-grey-950 px-4 py-12">
            <div className="w-full max-w-md space-y-8">
                {/* Brand */}
                <div className="text-center">
                    <h1 className="text-2xl font-semibold text-grey-50">Apex</h1>
                    <p className="mt-1 text-sm text-grey-400">Create your account</p>
                </div>

                {/* Role selection */}
                {!role ? (
                    <div className="space-y-4">
                        <p className="text-sm font-medium text-grey-300 text-center">
                            What brings you to Apex?
                        </p>
                        <div className="grid grid-cols-2 gap-3">
                            <RoleCard
                                role="trainer"
                                selected={false}
                                onClick={() => setRole('trainer')}
                            />
                            <RoleCard
                                role="client"
                                selected={false}
                                onClick={() => setRole('client')}
                            />
                        </div>
                        <p className="text-center text-xs text-grey-600">
                            Already have an account?{' '}
                            <button
                                type="button"
                                onClick={() => navigate({ to: ROUTES.login })}
                                className="text-brand-400 hover:text-brand-300 underline-offset-2 hover:underline"
                            >
                                Sign in
                            </button>
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6">
                        {/* Selected role + back */}
                        <div className="flex items-center gap-3">
                            <button
                                type="button"
                                onClick={() => setRole(null)}
                                className="flex items-center justify-center w-8 h-8 rounded-lg text-grey-500 hover:text-grey-200 hover:bg-grey-800 transition-colors cursor-pointer"
                                aria-label="Back to role selection"
                            >
                                <ArrowLeft size={15} />
                            </button>
                            <div
                                className={cn(
                                    'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium',
                                    'bg-brand-500/10 text-brand-300',
                                )}
                            >
                                {role === 'trainer' ? <Dumbbell size={13} /> : <Users size={13} />}
                                {role === 'trainer' ? 'Trainer' : 'Client'}
                            </div>
                            <span className="text-xs text-grey-500">
                                {role === 'trainer'
                                    ? 'Looking for clients'
                                    : 'Looking for a trainer'}
                            </span>
                        </div>

                        {/* Registration form */}
                        <form
                            onSubmit={(e) => {
                                e.preventDefault()
                                form.handleSubmit()
                            }}
                            className="space-y-4"
                        >
                            {/* Name row */}
                            <div className="grid grid-cols-2 gap-3">
                                <form.Field name="first_name">
                                    {(field) => (
                                        <div>
                                            <Label htmlFor="first_name">First name</Label>
                                            <Input
                                                id="first_name"
                                                placeholder="Jane"
                                                value={field.state.value}
                                                onChange={(e) => field.handleChange(e.target.value)}
                                                onBlur={field.handleBlur}
                                                autoFocus
                                            />
                                            <FieldError errors={field.state.meta.errors} />
                                        </div>
                                    )}
                                </form.Field>
                                <form.Field name="last_name">
                                    {(field) => (
                                        <div>
                                            <Label htmlFor="last_name">Last name</Label>
                                            <Input
                                                id="last_name"
                                                placeholder="Smith"
                                                value={field.state.value}
                                                onChange={(e) => field.handleChange(e.target.value)}
                                                onBlur={field.handleBlur}
                                            />
                                            <FieldError errors={field.state.meta.errors} />
                                        </div>
                                    )}
                                </form.Field>
                            </div>

                            <form.Field name="email">
                                {(field) => (
                                    <div>
                                        <Label htmlFor="email">Email</Label>
                                        <Input
                                            id="email"
                                            type="email"
                                            autoComplete="email"
                                            placeholder="you@example.com"
                                            value={field.state.value}
                                            onChange={(e) => field.handleChange(e.target.value)}
                                            onBlur={field.handleBlur}
                                        />
                                        <FieldError errors={field.state.meta.errors} />
                                    </div>
                                )}
                            </form.Field>

                            <form.Field name="password1">
                                {(field) => (
                                    <div>
                                        <Label htmlFor="password1">Password</Label>
                                        <Input
                                            id="password1"
                                            type="password"
                                            autoComplete="new-password"
                                            placeholder="8+ characters"
                                            value={field.state.value}
                                            onChange={(e) => field.handleChange(e.target.value)}
                                            onBlur={field.handleBlur}
                                        />
                                        <FieldError errors={field.state.meta.errors} />
                                    </div>
                                )}
                            </form.Field>

                            <form.Field name="password2">
                                {(field) => (
                                    <div>
                                        <Label htmlFor="password2">Confirm password</Label>
                                        <Input
                                            id="password2"
                                            type="password"
                                            autoComplete="new-password"
                                            placeholder="Repeat password"
                                            value={field.state.value}
                                            onChange={(e) => field.handleChange(e.target.value)}
                                            onBlur={field.handleBlur}
                                        />
                                        <FieldError errors={field.state.meta.errors} />
                                    </div>
                                )}
                            </form.Field>

                            <form.Subscribe selector={(s) => s.isSubmitting}>
                                {(isSubmitting) => (
                                    <Button
                                        type="submit"
                                        disabled={isSubmitting}
                                        className="w-full"
                                    >
                                        {isSubmitting ? 'Creating account…' : 'Create account'}
                                    </Button>
                                )}
                            </form.Subscribe>
                        </form>

                        <p className="text-center text-xs text-grey-600">
                            Already have an account?{' '}
                            <button
                                type="button"
                                onClick={() => navigate({ to: ROUTES.login })}
                                className="text-brand-400 hover:text-brand-300 underline-offset-2 hover:underline"
                            >
                                Sign in
                            </button>
                        </p>
                    </div>
                )}
            </div>
        </div>
    )
}
