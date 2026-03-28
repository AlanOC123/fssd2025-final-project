import { createFileRoute, redirect } from '@tanstack/react-router'
import { ROUTES } from '@/app/constants'
import { RegisterPage } from '@/features/auth/components/RegistrationPage'

/**
 * @fileoverview Defines the public registration route.
 * This module ensures that authenticated users are redirected to their
 * respective dashboards if they attempt to access the registration page.
 */

/**
 * Route configuration for the user registration page.
 * Maps the '/register' endpoint.
 */
export const Route = createFileRoute('/register')({
    /**
     * Prevents authenticated users from accessing the registration view.
     *
     * @param {!{context: !Object}} args The route arguments containing the
     * application context.
     * @throws {!Object} A redirect object if the user is already authenticated,
     * sending them to the appropriate dashboard based on their role.
     */
    beforeLoad: ({ context }) => {
        if (context.isAuthenticated) {
            throw redirect({
                to: context.isClient ? ROUTES.client.dashboard : ROUTES.trainer.dashboard,
            })
        }
    },

    /**
     * Component to render for this route.
     */
    component: RegisterPage,
})
