import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { RegisterPage } from '@/features/auth/components/RegistrationPage'

export const Route = createFileRoute('/register')({
    beforeLoad: ({ context }) => {
        if (context.isAuthenticated) {
            throw redirect({
                to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },
    component: RegisterPage,
})
