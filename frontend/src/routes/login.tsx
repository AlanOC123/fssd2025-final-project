import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { LoginPage } from '@/features/auth/components/LoginPage'

export const Route = createFileRoute('/login')({
    beforeLoad: ({ context }) => {
        if (context.isAuthenticated) {
            throw redirect({
                to: context.role === 'client' ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },
    component: LoginPage,
})
