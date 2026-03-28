import { createFileRoute } from '@tanstack/react-router'
import { TermsPage } from '@/features/static/components/TermsPage'

/**
 * Route definition for the application terms and conditions page.
 *
 * This route is nested under the authenticated layout (`/_auth`) and
 * serves the legal terms and conditions content.
 */
export const Route = createFileRoute('/_auth/terms')({
    /**
     * The visual component rendered when this route is active.
     */
    component: TermsPage,
})
