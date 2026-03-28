import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { PaginatedResponse } from '@/shared/types/base'
import type { TrainerMatchProfile } from '../types'

/** Cache key used for trainer-related queries. */
export const TRAINERS_QUERY_KEY = ['trainers'] as const

/**
 * API methods for searching trainers and managing membership requests.
 */
export const trainersApi = {
    /**
     * Retrieves a paginated list of trainers, optionally filtered by a search string.
     *
     * @param search Optional search query to filter trainers by name or keywords.
     * @return A promise resolving to a paginated response containing trainer profiles.
     */
    list: (search?: string): Promise<PaginatedResponse<TrainerMatchProfile>> =>
        api.get<PaginatedResponse<TrainerMatchProfile>>('/users/find-trainers/', {
            params: search ? { search } : undefined,
        }),

    /**
     * Initiates a membership request to a specific trainer.
     *
     * @param trainerId The unique identifier of the trainer to request membership from.
     * @return A promise that resolves when the request has been successfully posted.
     */
    requestMembership: (trainerId: string): Promise<void> =>
        api.post<void>('/users/trainer-client-memberships/request/', { trainer_id: trainerId }),
}

/**
 * Creates configuration options for the TanStack Query hook to fetch trainers.
 *
 * @param search Optional search term used for filtering and cache invalidation.
 * @return Query options including the generated query key and fetch function.
 */
export const trainersQueryOptions = (search?: string) =>
    queryOptions({
        queryKey: [...TRAINERS_QUERY_KEY, search ?? ''],
        queryFn: () => trainersApi.list(search || undefined),
        staleTime: 30 * 1000,
    })
