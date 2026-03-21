import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { ForgotPasswordPage } from '@/features/auth/components/ForgotPasswordPage'

export const Route = createFileRoute('/forgot-password')({
    beforeLoad: ({ context }) => {
        if (context.isAuthenticated) {
            throw redirect({
                to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },
    component: ForgotPasswordPage,
})
