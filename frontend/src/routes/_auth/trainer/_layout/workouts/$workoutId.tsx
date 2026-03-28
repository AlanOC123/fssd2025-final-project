import { createFileRoute } from '@tanstack/react-router'
import { TrainerWorkoutDetail } from '@/features/workouts/components/TrainerWorkoutDetail'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

/**
 * @fileoverview Defines the route for the trainer's view of a specific workout.
 * This module manages the dynamic routing and pre-fetching of workout details
 * based on the provided workout identifier.
 */

/**
 * Route definition for the trainer workout detail view.
 * Maps the dynamic '$workoutId' path within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/workouts/$workoutId')({
    /**
     * Pre-fetches the detailed information for a specific workout.
     *
     * @param context Object containing the route context and TanStack query client.
     * @param params Object containing the route parameters, specifically workoutId.
     * @return {Promise<unknown>} A promise that resolves when the workout details
     * are successfully cached.
     * @throws {Error} If the workout detail query fails to resolve.
     */
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),

    /**
     * Functional component for the TrainerWorkoutDetail route.
     * Extracts the workout ID from the route state and renders the trainer-specific
     * detailed view.
     *
     * @return {JSX.Element} The rendered trainer workout detail component.
     */
    component: function TrainerWorkoutDetailRoute() {
        const { workoutId } = Route.useParams()
        return <TrainerWorkoutDetail workoutId={workoutId} />
    },
})
