import { queryOptions } from '@tanstack/react-query'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import type { Membership } from '../types'

/**
 * Filter parameters for retrieving memberships.
 */
export interface MembershipsParams {
    /** The status to filter by (e.g., 'Active', 'Pending'). */
    status?: string
}

/**
 * Generates a consistent query key for memberships based on provided parameters.
 *
 * @param params Optional filters for the membership list.
 * @return A read-only array used as a TanStack Query key.
 */
export const MEMBERSHIP_QUERY_KEY = (params?: MembershipsParams) =>
    ['memberships', params ?? {}] as const

/**
 * API methods for managing trainer-client memberships.
 */
export const membershipsApi = {
    /**
     * Retrieves a paginated list of memberships.
     *
     * @param params Optional filtering parameters.
     * @return A promise resolving to a paginated response of Membership objects.
     */
    list: (params?: MembershipsParams) =>
        api.get<PaginatedResponse<Membership>>('/users/trainer-client-memberships/', { params }),

    /**
     * Retrieves details for a specific membership.
     *
     * @param id The unique identifier of the membership.
     * @return A promise resolving to the Membership details.
     */
    get: (id: string) => api.get<Membership>(`/users/trainer-client-memberships/${id}/`),

    /**
     * Accepts a pending membership request.
     *
     * @param id The unique identifier of the membership.
     * @return A promise resolving to the updated Membership.
     */
    accept: (id: string) => api.post<Membership>(`/users/trainer-client-memberships/${id}/accept/`),

    /**
     * Rejects a pending membership request.
     *
     * @param id The unique identifier of the membership.
     * @return A promise resolving to the updated Membership.
     */
    reject: (id: string) => api.post<Membership>(`/users/trainer-client-memberships/${id}/reject/`),

    /**
     * Dissolves an existing membership between a trainer and a client.
     *
     * @param id The unique identifier of the membership.
     * @return A promise resolving to the updated Membership.
     */
    dissolve: (id: string) =>
        api.post<Membership>(`/users/trainer-client-memberships/${id}/dissolve/`),
}

/**
 * Creates query options for fetching a list of memberships.
 *
 * @param params Optional filtering parameters.
 * @return Configuration object for TanStack Query.
 */
export const membershipsQueryOptions = (params?: MembershipsParams) =>
    queryOptions({
        queryKey: MEMBERSHIP_QUERY_KEY(params),
        queryFn: () => membershipsApi.list(params),
    })

/**
 * Creates query options specifically for active memberships.
 *
 * @return Configuration object for TanStack Query filtered by 'Active' status.
 */
export const activeMembershipsQueryOptions = () => membershipsQueryOptions({ status: 'Active' })

/**
 * Creates query options for fetching a single membership's details.
 *
 * @param id The unique identifier of the membership.
 * @return Configuration object for TanStack Query.
 */
export const membershipDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['memberships', id],
        queryFn: () => membershipsApi.get(id),
    })
