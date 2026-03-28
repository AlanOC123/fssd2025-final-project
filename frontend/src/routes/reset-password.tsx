import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { RegisterPage } from '@/features/auth/components/RegistrationPage'

/**
 * Route definition for the registration page.
 *
 * This route handles user account creation and prevents already
 * authenticated users from accessing the registration form by redirecting
 * them to their respective dashboards.
 */
export const Route = createFileRoute('/reset-password')({
    /**
     * Validates authentication state before the registration page is loaded.
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
        if (context.isAuthenticated) {
            throw redirect({
                to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },
    component: RegisterPage,
})
