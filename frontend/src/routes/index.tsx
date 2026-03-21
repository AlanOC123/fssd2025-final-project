import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'

export const Route = createFileRoute('/')({
    beforeLoad: ({ context }) => {
        if (!context.isAuthenticated) {
            throw redirect({ to: ROUTES.login })
        }
        throw redirect({
            to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
        })
    },
})
