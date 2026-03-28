import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { ForgotPasswordPage } from '@/features/auth/components/ForgotPasswordPage'

/**
 * Route definition for the forgot password page.
 *
 * This route handles the password recovery flow and prevents authenticated
 * users from accessing the recovery form by redirecting them to their
 * respective dashboards based on their account type.
 */
export const Route = createFileRoute('/forgot-password')({
    /**
     * Validates authentication state before loading the forgot password page.
     *
     * @param {{
     * context: {
     * isAuthenticated: boolean,
     * isClient: boolean,
     * }
     * }} options The route transition options containing authentication context.
     * @throws {ReturnType<typeof redirect>} Redirects to the appropriate dashboard
     * if the user is already authenticated.
     */
    beforeLoad: ({ context }) => {
        // Development-only logging to trace route guard execution.
        // Use of import.meta.env.DEV is required by project standards.
        if (import.meta.env.DEV) {
            console.log('Forgot password route access check:', {
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
    component: ForgotPasswordPage,
})
