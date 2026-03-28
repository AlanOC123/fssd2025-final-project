import { createFileRoute } from '@tanstack/react-router'
import { SitemapPage } from '@/features/static/components/SitemapPage'

/**
 * Route definition for the application sitemap page.
 *
 * This route is nested under the authenticated layout (`/_auth`) and
 * provides a structural overview of the application's available pages.
 */
export const Route = createFileRoute('/_auth/sitemap')({
    /**
     * The visual component rendered when this route is active.
     */
    component: SitemapPage,
})
