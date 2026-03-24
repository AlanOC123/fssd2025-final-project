import { createFileRoute } from '@tanstack/react-router'
import { TermsPage } from '@/features/static/components/TermsPage'

export const Route = createFileRoute('/_auth/terms')({
    component: TermsPage,
})
