import { useForm } from '@tanstack/react-form'
import { useNavigate } from '@tanstack/react-router'
import { z } from 'zod'
import { useAuth } from '@/shared/hooks/useAuth'
import { useAuthStore } from '../store'
import { ROUTES } from '@/app/constants'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { toastApiError } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'
import { router } from '@/app/router'

const loginSchema = z.object({
    email: z.email('Please enter a valid email'),
    password: z.string().min(1, 'Password is required'),
})

export function LoginPage() {
    const { login, isLoading } = useAuth()
    const navigate = useNavigate()

    const form = useForm({
        defaultValues: {
            email: '',
            password: '',
        },
        validators: {
            onSubmit: loginSchema,
        },
        onSubmit: async ({ value }) => {
            const { error } = await tryCatch(login(value));

            if (error) {
                toastApiError(error, 'Login failed');
                return
            }

            const isClient = useAuthStore.getState().user?.is_client

            await navigate({
                to: isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })

            router.invalidate()
        },
    })

    return (
        <div className="min-h-dvh flex items-center justify-center bg-grey-950 px-4">
            <div className="w-full max-w-sm space-y-8">
                {/* Brand */}
                <div className="text-center">
                    <h1 className="text-2xl font-semibold text-grey-50">Apex</h1>
                    <p className="mt-1 text-sm text-grey-400">Sign in to your account</p>
                </div>

                {/* Form */}
                <form
                    onSubmit={(e) => {
                        e.preventDefault()
                        form.handleSubmit()
                    }}
                    className="space-y-4"
                >
                    <form.Field name="email">
                        {(field) => (
                            <div className="space-y-1.5">
                                <Label htmlFor="email">Email</Label>
                                <Input
                                    id="email"
                                    type="email"
                                    autoComplete="email"
                                    placeholder="you@example.com"
                                    value={field.state.value}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    onBlur={field.handleBlur}
                                    aria-invalid={field.state.meta.errors.length > 0}
                                />
                                {field.state.meta.errors[0] && (
                                    <p className="text-xs text-destructive">
                                        {field.state.meta.errors[0].message}
                                    </p>
                                )}
                            </div>
                        )}
                    </form.Field>

                    <form.Field name="password">
                        {(field) => (
                            <div className="space-y-1.5">
                                <Label htmlFor="password">Password</Label>
                                <Input
                                    id="password"
                                    type="password"
                                    autoComplete="current-password"
                                    placeholder="••••••••"
                                    value={field.state.value}
                                    onChange={(e) => field.handleChange(e.target.value)}
                                    onBlur={field.handleBlur}
                                    aria-invalid={field.state.meta.errors.length > 0}
                                />
                                {field.state.meta.errors[0] && (
                                    <p className="text-xs text-destructive">
                                        {field.state.meta.errors[0].message}
                                    </p>
                                )}
                            </div>
                        )}
                    </form.Field>

                    {/* API-level error */}
                    <form.Subscribe selector={(s) => s.errors}>
                        {(errors) =>
                            errors.length > 0 && (
                                <p className="text-sm text-destructive">{String(errors[0])}</p>
                            )
                        }
                    </form.Subscribe>

                    <form.Subscribe selector={(s) => s.isSubmitting}>
                        {(isSubmitting) => (
                            <Button
                                type="submit"
                                disabled={isSubmitting || isLoading}
                                className="w-full"
                            >
                                {isSubmitting || isLoading ? 'Signing in...' : 'Sign in'}
                            </Button>
                        )}
                    </form.Subscribe>
                </form>
            </div>
        </div>
    )
}
