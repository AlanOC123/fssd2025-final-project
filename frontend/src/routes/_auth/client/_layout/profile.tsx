import { createFileRoute } from '@tanstack/react-router'
import { ClientProfile } from '@/features/profile/components/ClientProfile'

/**
 * @fileoverview Defines the route configuration for the client profile page.
 * This route is restricted to authenticated clients and utilizes the standard
 * client layout.
 */

/**
 * Route definition for the '/profile' path.
 * Renders the ClientProfile component, providing the interface for users to
 * manage their personal data and account settings.
 */
export const Route = createFileRoute('/_auth/client/_layout/profile')({
    component: ClientProfile,
})
