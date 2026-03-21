import { createFileRoute } from '@tanstack/react-router'
import { FindTrainer } from '@/features/trainers/components/FindTrainer'

export const Route = createFileRoute('/_auth/client/_layout/find-trainer')({
    component: FindTrainer,
})
