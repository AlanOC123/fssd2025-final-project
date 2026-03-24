import { createFileRoute } from '@tanstack/react-router'
import { SitemapPage } from '@/features/static/components/SitemapPage'

export const Route = createFileRoute('/_auth/sitemap')({
    component: SitemapPage,
})
