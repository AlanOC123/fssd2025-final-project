import { createFileRoute } from '@tanstack/react-router'
import { AboutPage } from '@/features/static/components/AboutPage'

/**
 * Route definition for the application's about page.
 *
 * This route is nested under the authenticated layout (`/_auth`) and
 * serves the static informational content of the application.
 */
export const Route = createFileRoute('/_auth/about')({
    /**
     * The visual component rendered when this route is active.
     */
    component: AboutPage,
})
