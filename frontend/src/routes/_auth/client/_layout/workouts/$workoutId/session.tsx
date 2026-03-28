import { createFileRoute } from '@tanstack/react-router'
import { WorkoutSession } from '@/features/workouts/components/WorkoutSession'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

/**
 * @fileoverview Defines the route for an active workout session.
 * This module ensures the specific workout details are pre-fetched based on the
 * workout ID parameter before the session interface is rendered.
 */

/**
 * Route configuration for the workout session path.
 * Maps the dynamic '$workoutId/session' endpoint within the authenticated
 * client layout.
 */
export const Route = createFileRoute('/_auth/client/_layout/workouts/$workoutId/session')({
    /**
     * Pre-fetches the detailed data for a specific workout session.
     *
     * @param context Object containing the route context and query client.
     * @param params Object containing the route parameters, specifically workoutId.
     * @return {Promise<unknown>} A promise that resolves when the workout details
     * are cached.
     * @throws {Error} If the workout detail query fails to resolve.
     */
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),

    /**
     * Functional component wrapper for the WorkoutSession.
     * Extracts the workout ID from the route parameters and passes it to the
     * session component.
     *
     * @return {JSX.Element} The rendered workout session component.
     */
    component: function WorkoutSessionRoute() {
        const { workoutId } = Route.useParams()
        return <WorkoutSession workoutId={workoutId} />
    },
})
