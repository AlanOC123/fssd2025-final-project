import { createFileRoute } from '@tanstack/react-router'
import { AboutPage } from '@/features/static/components/AboutPage'

export const Route = createFileRoute('/_auth/about')({
    component: AboutPage,
})
