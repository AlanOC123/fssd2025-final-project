import { createFileRoute } from '@tanstack/react-router'
import { FindTrainer } from '@/features/trainers/components/FindTrainer'

/**
 * @fileoverview Defines the routing configuration for the trainer search feature.
 * This route is nested under the authenticated client layout.
 */

/**
 * Route definition for the 'find-trainer' path.
 * Renders the FindTrainer component to allow users to browse and select
 * fitness professionals.
 */
export const Route = createFileRoute('/_auth/client/_layout/find-trainer')({
    component: FindTrainer,
})
