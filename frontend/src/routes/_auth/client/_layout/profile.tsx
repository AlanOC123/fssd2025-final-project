import { createFileRoute } from '@tanstack/react-router'
import { ClientProfile } from '@/features/profile/components/ClientProfile'

export const Route = createFileRoute('/_auth/client/_layout/profile')({
    component: ClientProfile,
})
