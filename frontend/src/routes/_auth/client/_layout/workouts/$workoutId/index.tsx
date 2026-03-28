import { createFileRoute } from '@tanstack/react-router'
import { WorkoutDetail } from '@/features/workouts/components/WorkoutDetail'
import { workoutDetailQueryOptions } from '@/features/workouts/api'

/**
 * @fileoverview Defines the routing logic and data loading for the workout
 * detail view within the client dashboard.
 */

/**
 * Route definition for viewing detailed workout information.
 * This route is nested under the authenticated client layout and handles
 * dynamic ID parameters for specific workout lookups.
 */
export const Route = createFileRoute('/_auth/client/_layout/workouts/$workoutId/')({
    /**
     * Pre-fetches specific workout details into the query cache.
     *
     * @param context Object containing the route context and TanStack query client.
     * @param params Object containing route parameters, including the workoutId.
     * @return {Promise<unknown>} A promise that resolves when the workout data is
     * successfully cached.
     * @throws {Error} If the workout detail query fails to resolve or the API
     * is unreachable.
     */
    loader: ({ context: { queryClient }, params: { workoutId } }) =>
        queryClient.ensureQueryData(workoutDetailQueryOptions(workoutId)),

    /**
     * Functional component serving as the entry point for the workout detail view.
     * Extracts the workout ID from the current route state to initialize the
     * Detail component.
     *
     * @return {JSX.Element} The rendered workout detail view.
     */
    component: function WorkoutDetailRoute() {
        const { workoutId } = Route.useParams()
        return <WorkoutDetail workoutId={workoutId} />
    },
})
