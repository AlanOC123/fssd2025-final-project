import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { PaginatedResponse } from '@/shared/types/base'
import type { ProgramListItem, ProgramDetail, ProgramStatusCode } from '../types'

export interface ProgramsParams {
    status?: ProgramStatusCode
    trainer_client_membership?: string
}

export const PROGRAM_QUERY_KEY = (params?: ProgramsParams) => ['programs', params ?? {}] as const

export const programsApi = {
    list: (params?: ProgramsParams) =>
        api.get<PaginatedResponse<ProgramListItem>>('/programs/programs/', { params }),

    get: (id: string) =>
        api.get<ProgramDetail>(`/programs/programs/${id}/`)
}

export const programsQueryOptions = (params?: ProgramsParams) =>
    queryOptions({ queryKey: PROGRAM_QUERY_KEY(params), queryFn: () => programsApi.list(params) })

export const activeProgramsQueryOptions = () =>
    programsQueryOptions({ status: 'IN_PROGRESS' })

export const programDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['programs', id],
        queryFn: () => programsApi.get(id)
    })
