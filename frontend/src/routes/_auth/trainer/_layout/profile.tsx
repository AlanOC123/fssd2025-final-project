import { createFileRoute } from '@tanstack/react-router'
import { TrainerProfile } from '@/features/profile/components/TrainerProfile'

/**
 * @fileoverview Defines the routing configuration for the trainer's personal
 * profile section. This module maps the profile endpoint to its corresponding
 * UI component within the authenticated trainer layout.
 */

/**
 * Route definition for the trainer profile page.
 * * This constant defines the path and component mapping for the trainer profile.
 * It is integrated into the authenticated trainer layout hierarchy.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/profile')({
    component: TrainerProfile,
})
