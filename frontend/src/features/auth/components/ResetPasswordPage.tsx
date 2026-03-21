import { useForm } from '@tanstack/react-form'
import { useNavigate, useSearch } from '@tanstack/react-router'
import { z } from 'zod'
import { CheckCircle, AlertCircle } from 'lucide-react'
import { authApi } from '@/features/auth/api'
import { ROUTES } from '@/app/constants'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { toastApiError } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'
import { useState } from 'react'

const schema = z
    .object({
        new_password1: z.string().min(8, 'Password must be at least 8 characters'),
        new_password2: z.string().min(1, 'Please confirm your password'),
    })
    .refine((d) => d.new_password1 === d.new_password2, {
        message: 'Passwords do not match',
        path: ['new_password2'],
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

export function ResetPasswordPage() {
    const [done, setDone] = useState(false)
    const navigate = useNavigate()

    // Read uid and token from the URL query string
    // The email link from Django is: /reset-password?uid=...&token=...
    const search = useSearch({ strict: false }) as { uid?: string; token?: string }
    const uid = search.uid ?? ''
    const token = search.token ?? ''

    const missingParams = !uid || !token

    const form = useForm({
        defaultValues: { new_password1: '', new_password2: '' },
        validators: { onSubmit: schema },
        onSubmit: async ({ value }) => {
            const { error } = await tryCatch(authApi.resetPasswordConfirm({ uid, token, ...value }))

            if (error) {
                toastApiError(error, 'Failed to reset password')
                return
            }

            setDone(true)
        },
    })

    return (
        <div className="min-h-dvh flex items-center justify-center bg-grey-950 px-4">
            <div className="w-full max-w-sm space-y-8">
                {/* Brand */}
                <div className="text-center">
                    <h1 className="text-2xl font-semibold text-grey-50">Apex</h1>
                    <p className="mt-1 text-sm text-grey-400">Choose a new password</p>
                </div>

                {missingParams ? (
                    /* Invalid link */
                    <div className="text-center space-y-4">
                        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-danger-500/10 text-danger-400 mx-auto">
                            <AlertCircle size={20} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-grey-100">Invalid reset link</p>
                            <p className="text-xs text-grey-500 mt-1">
                                This link is missing required parameters. Request a new one.
                            </p>
                        </div>
                        <Button
                            size="sm"
                            onClick={() => navigate({ to: ROUTES.forgotPassword })}
                            className="mx-auto"
                        >
                            Request new link
                        </Button>
                    </div>
                ) : done ? (
                    /* Success */
                    <div className="text-center space-y-4">
                        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-success-500/10 text-success-400 mx-auto">
                            <CheckCircle size={20} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-grey-100">Password updated</p>
                            <p className="text-xs text-grey-500 mt-1">
                                You can now sign in with your new password.
                            </p>
                        </div>
                        <Button
                            size="sm"
                            onClick={() => navigate({ to: ROUTES.login })}
                            className="mx-auto"
                        >
                            Sign in
                        </Button>
                    </div>
                ) : (
                    /* Form */
                    <form
                        onSubmit={(e) => {
                            e.preventDefault()
                            form.handleSubmit()
                        }}
                        className="space-y-4"
                    >
                        <form.Field name="new_password1">
                            {(field) => (
                                <div>
                                    <Label htmlFor="new_password1">New password</Label>
                                    <Input
                                        id="new_password1"
                                        type="password"
                                        autoComplete="new-password"
                                        placeholder="8+ characters"
                                        value={field.state.value}
                                        onChange={(e) => field.handleChange(e.target.value)}
                                        onBlur={field.handleBlur}
                                        autoFocus
                                    />
                                    <FieldError errors={field.state.meta.errors} />
                                </div>
                            )}
                        </form.Field>

                        <form.Field name="new_password2">
                            {(field) => (
                                <div>
                                    <Label htmlFor="new_password2">Confirm new password</Label>
                                    <Input
                                        id="new_password2"
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
                                <Button type="submit" disabled={isSubmitting} className="w-full">
                                    {isSubmitting ? 'Updating…' : 'Update password'}
                                </Button>
                            )}
                        </form.Subscribe>
                    </form>
                )}
            </div>
        </div>
    )
}
