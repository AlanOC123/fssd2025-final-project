import { createFileRoute } from '@tanstack/react-router'
import { ResetPasswordPage } from '@/features/auth/components/ResetPasswordPage'

export const Route = createFileRoute('/reset-password')({
    // No auth check — this must be accessible when logged out
    validateSearch: (search: Record<string, unknown>) => ({
        uid: (search.uid as string) ?? '',
        token: (search.token as string) ?? '',
    }),
    component: ResetPasswordPage,
})
