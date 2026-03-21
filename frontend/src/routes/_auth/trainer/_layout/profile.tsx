import { createFileRoute } from '@tanstack/react-router'
import { TrainerProfile } from '@/features/profile/components/TrainerProfile'

export const Route = createFileRoute('/_auth/trainer/_layout/profile')({
    component: TrainerProfile,
})
