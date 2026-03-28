import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { LoginPage } from '@/features/auth/components/LoginPage'

/**
 * Route definition for the login page.
 *
 * This route handles user authentication entry and prevents already
 * authenticated users from accessing the login form by redirecting them
 * to their respective dashboards.
 */
export const Route = createFileRoute('/login')({
    /**
     * Validates authentication state before the login page is loaded.
     *
     * @param {{
     * context: {
     * isAuthenticated: boolean;
     * isClient: boolean;
     * }
     * }} options The route transition options containing authentication context.
     * @throws {ReturnType<typeof redirect>} Redirects to the appropriate dashboard
     * if the user is already authenticated.
     */
    beforeLoad: ({ context }) => {
        // Development-only logging to trace navigation flow.
        if (import.meta.env.DEV) {
            console.log('Login route access check:', {
                isAuthenticated: context.isAuthenticated,
                isClient: context.isClient,
            })
        }

        if (context.isAuthenticated) {
            throw redirect({
                to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },
    component: LoginPage,
})
