import { ROUTES } from '@/app/constants'
import { createFileRoute, redirect, Outlet } from '@tanstack/react-router'
import { useAuthStore } from '@/features/auth/store'

export const Route = createFileRoute('/_auth')({
    beforeLoad: () => {
        const isAuthenticated = useAuthStore.getState().isAuthenticated
        if (!isAuthenticated) {
            throw redirect({ to: ROUTES.login })
        }
    },
    component: Outlet,
})
