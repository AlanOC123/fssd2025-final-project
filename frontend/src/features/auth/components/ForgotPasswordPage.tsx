import { useState } from 'react'
import { useForm } from '@tanstack/react-form'
import { useNavigate } from '@tanstack/react-router'
import { z } from 'zod'
import { ArrowLeft, Mail } from 'lucide-react'
import { authApi } from '@/features/auth/api'
import { ROUTES } from '@/app/constants'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { toastApiError } from '@/shared/utils/toast'
import { tryCatch } from '@/shared/utils/tryCatch'

const schema = z.object({
    email: z.email('Please enter a valid email'),
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

export function ForgotPasswordPage() {
    const [sent, setSent] = useState(false)
    const [submittedEmail, setSubmittedEmail] = useState('')
    const navigate = useNavigate()

    const form = useForm({
        defaultValues: { email: '' },
        validators: { onSubmit: schema },
        onSubmit: async ({ value }) => {
            const { error } = await tryCatch(authApi.forgotPassword(value.email))

            if (error) {
                toastApiError(error, 'Failed to send reset email')
                return
            }

            setSubmittedEmail(value.email)
            setSent(true)
        },
    })

    return (
        <div className="min-h-dvh flex items-center justify-center bg-grey-950 px-4">
            <div className="w-full max-w-sm space-y-8">
                {/* Brand */}
                <div className="text-center">
                    <h1 className="text-2xl font-semibold text-grey-50">Apex</h1>
                    <p className="mt-1 text-sm text-grey-400">Reset your password</p>
                </div>

                {sent ? (
                    /* Success state */
                    <div className="text-center space-y-4">
                        <div className="flex items-center justify-center w-12 h-12 rounded-full bg-brand-500/10 text-brand-400 mx-auto">
                            <Mail size={20} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-grey-100">Check your email</p>
                            <p className="text-xs text-grey-500 mt-1">
                                We sent a reset link to{' '}
                                <span className="text-grey-300">{submittedEmail}</span>
                            </p>
                        </div>
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => navigate({ to: ROUTES.login })}
                            className="text-grey-500 hover:text-grey-200 gap-1.5"
                        >
                            <ArrowLeft size={13} />
                            Back to sign in
                        </Button>
                    </div>
                ) : (
                    /* Form */
                    <div className="space-y-6">
                        <p className="text-sm text-grey-400 text-center">
                            Enter your email and we'll send you a link to reset your password.
                        </p>

                        <form
                            onSubmit={(e) => {
                                e.preventDefault()
                                form.handleSubmit()
                            }}
                            className="space-y-4"
                        >
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
                                            autoFocus
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
                                        {isSubmitting ? 'Sending…' : 'Send reset link'}
                                    </Button>
                                )}
                            </form.Subscribe>
                        </form>

                        <p className="text-center text-xs text-grey-600">
                            Remember it?{' '}
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
