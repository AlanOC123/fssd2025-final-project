import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { PaginatedResponse } from '@/shared/types/base'
import type { TrainerMatchProfile } from '../types'

export const TRAINERS_QUERY_KEY = ['trainers'] as const

export const trainersApi = {
    list: (search?: string): Promise<PaginatedResponse<TrainerMatchProfile>> =>
        api.get<PaginatedResponse<TrainerMatchProfile>>('/users/find-trainers/', {
            params: search ? { search } : undefined,
        }),

    requestMembership: (trainerId: string): Promise<void> =>
        api.post<void>('/users/trainer-client-memberships/request/', { trainer_id: trainerId }),
}

export const trainersQueryOptions = (search?: string) =>
    queryOptions({
        queryKey: [...TRAINERS_QUERY_KEY, search ?? ''],
        queryFn: () => trainersApi.list(search || undefined),
        staleTime: 30 * 1000,
    })
