import { queryOptions } from '@tanstack/react-query'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import type { Membership } from '../types'

export interface MembershipsParams {
    status?: string
}

export const MEMBERSHIP_QUERY_KEY = (params?: MembershipsParams) =>
    ['memberships', params ?? {}] as const

export const membershipsApi = {
    list: (params?: MembershipsParams) =>
        api.get<PaginatedResponse<Membership>>('/users/trainer-client-memberships/', { params }),

    get: (id: string) => api.get<Membership>(`/users/trainer-client-memberships/${id}/`),

    accept: (id: string) => api.post<Membership>(`/users/trainer-client-memberships/${id}/accept/`),

    reject: (id: string) => api.post<Membership>(`/users/trainer-client-memberships/${id}/reject/`),

    dissolve: (id: string) =>
        api.post<Membership>(`/users/trainer-client-memberships/${id}/dissolve/`),
}

export const membershipsQueryOptions = (params?: MembershipsParams) =>
    queryOptions({
        queryKey: MEMBERSHIP_QUERY_KEY(params),
        queryFn: () => membershipsApi.list(params),
    })

export const activeMembershipsQueryOptions = () =>
    membershipsQueryOptions({ status: 'Active' })

export const membershipDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['memberships', id],
        queryFn: () => membershipsApi.get(id),
    })
