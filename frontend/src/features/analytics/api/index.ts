import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { LoadHistoryEntry } from '../types'

/**
 * API methods for interacting with analytics endpoints.
 */
export const analyticsApi = {
    /**
     * Fetches the load history for a specific exercise within a training program.
     *
     * @param programId The unique identifier of the training program.
     * @param exerciseId The unique identifier of the specific exercise.
     * @return A promise resolving to an array of load history entries.
     */
    loadHistory: (programId: string, exerciseId: string) =>
        api.get<LoadHistoryEntry[]>(
            `/analytics/programs/${programId}/exercises/${exerciseId}/load-history/`,
        ),
}

/**
 * Creates configuration options for a TanStack Query to fetch load history.
 *
 * @param programId The unique identifier of the training program.
 * @param exerciseId The unique identifier of the specific exercise.
 * @return An object containing query configuration including key, function, and selector.
 */
export const loadHistoryQueryOptions = (programId: string, exerciseId: string) =>
    queryOptions({
        queryKey: ['analytics', 'load-history', programId, exerciseId],
        queryFn: () => analyticsApi.loadHistory(programId, exerciseId),
        select: (data) => (Array.isArray(data) ? data : []),
    })
