import { ROUTES } from '@/app/constants'
import { createFileRoute, redirect, Outlet } from '@tanstack/react-router'
import { useAuthStore } from '@/features/auth/store'

/**
 * Route definition for the authenticated layout wrapper.
 *
 * This route acts as a guard for all child routes under the `/_auth` path,
 * ensuring that only authenticated users can access them.
 */
export const Route = createFileRoute('/_auth')({
    /**
     * Validates authentication state before the route or its children are loaded.
     *
     * @throws {ReturnType<typeof redirect>} Redirects to the login page if the user
     * is not authenticated.
     */
    beforeLoad: () => {
        // In development mode, we ensure the store is accessible.
        if (import.meta.env.DEV) {
            console.log('Auth check initiated for route: /_auth')
        }

        const isAuthenticated = useAuthStore.getState().isAuthenticated
        if (!isAuthenticated) {
            throw redirect({ to: ROUTES.login })
        }
    },
    component: Outlet,
})
