import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'

/**
 * Route definition for the index path.
 *
 * This route serves as a central redirecting hub that evaluates the user's
 * authentication state and account type to route them to the appropriate
 * entry point.
 */
export const Route = createFileRoute('/')({
    /**
     * Handles redirection logic based on authentication status and user role.
     *
     * @param {{
     * context: {
     * isAuthenticated: boolean;
     * isClient: boolean;
     * }
     * }} options The route transition options containing authentication context.
     * @throws {ReturnType<typeof redirect>} Redirects to the login page for
     * unauthenticated users, or to the specific dashboard for authenticated users.
     */
    beforeLoad: ({ context }) => {
        // Development-only logging to trace navigation flow.
        if (import.meta.env.DEV) {
            console.log('Index route load context:', context)
        }

        if (!context.isAuthenticated) {
            throw redirect({ to: ROUTES.login })
        }

        throw redirect({
            to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
        })
    },
})
