import { createFileRoute } from '@tanstack/react-router'
import { ProgramDetail } from '@/features/programs/components/ProgramDetail'
import { programDetailQueryOptions } from '@/features/programs/api'

/**
 * @fileoverview Defines the routing configuration for the trainer's detailed
 * program view. This module manages the pre-fetching of program-specific
 * data based on the route parameter.
 */

/**
 * Route definition for the trainer program detail view.
 * Maps the dynamic '$programId' path within the authenticated trainer layout.
 */
export const Route = createFileRoute('/_auth/trainer/_layout/programs/$programId')({
    /**
     * Pre-fetches the detailed information for a specific training program.
     *
     * @param context Object containing the route context and query client.
     * @param params Object containing the route parameters, specifically programId.
     * @return {Promise<unknown>} A promise that resolves when the program data
     * is successfully cached.
     * @throws {Error} If the program detail query fails to resolve.
     */
    loader: ({ context: { queryClient }, params: { programId } }) =>
        queryClient.ensureQueryData(programDetailQueryOptions(programId)),

    /**
     * Functional component for the ProgramDetail route.
     * Extracts the program ID from the route state and renders the
     * detailed view component.
     *
     * @return {JSX.Element} The rendered program detail component.
     */
    component: function ProgramDetailRoute() {
        const { programId } = Route.useParams()
        return <ProgramDetail programId={programId} />
    },
})
