import { queryOptions } from '@tanstack/react-query'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import type {
    ProgramListItem,
    ProgramDetail,
    ProgramStatusCode,
    CreateProgramPayload,
    CreatePhasePayload,
} from '../types'

/**
 * Filter parameters for querying training programs.
 */
export interface ProgramsParams {
    /** Filter by the current lifecycle status of the program. */
    status?: ProgramStatusCode
    /** Filter by a specific trainer-client relationship identifier. */
    trainer_client_membership?: string
}

/**
 * Generates a unique query key for program-related requests.
 *
 * @param params Optional filters to include in the query key.
 * @return A read-only array used for TanStack Query caching.
 */
export const PROGRAM_QUERY_KEY = (params?: ProgramsParams) => ['programs', params ?? {}] as const

/**
 * API methods for interacting with training program endpoints.
 */
export const programsApi = {
    /**
     * Retrieves a paginated list of programs based on filter criteria.
     *
     * @param params Filtering criteria such as status or membership.
     * @return A promise resolving to a paginated list of program items.
     */
    list: (params?: ProgramsParams) =>
        api.get<PaginatedResponse<ProgramListItem>>('/programs/programs/', { params }),

    /**
     * Retrieves full details for a single program by its ID.
     *
     * @param id Unique identifier of the program.
     * @return A promise resolving to the detailed program data.
     */
    get: (id: string) => api.get<ProgramDetail>(`/programs/programs/${id}/`),

    /**
     * Submits data to create a new training program.
     *
     * @param payload The program definition data.
     * @return A promise resolving to the created program details.
     */
    create: (payload: CreateProgramPayload) =>
        api.post<ProgramDetail>('/programs/programs/', payload),

    /**
     * Creates a new phase within an existing program.
     *
     * @param payload The phase definition data.
     * @return A promise resolving to the updated program details.
     */
    createPhase: (payload: CreatePhasePayload) =>
        api.post<ProgramDetail>('/programs/program-phases/', payload),
}

/**
 * Creates configuration options for fetching a list of programs via TanStack Query.
 *
 * @param params Optional filtering parameters.
 * @return Query configuration object.
 */
export const programsQueryOptions = (params?: ProgramsParams) =>
    queryOptions({
        queryKey: PROGRAM_QUERY_KEY(params),
        queryFn: () => programsApi.list(params),
    })

/**
 * Pre-configured query options for programs that are currently in progress.
 *
 * @return Query configuration object filtered by 'IN_PROGRESS' status.
 */
export const activeProgramsQueryOptions = () => programsQueryOptions({ status: 'IN_PROGRESS' })

/**
 * Creates configuration options for fetching a single program's details.
 *
 * @param id Unique identifier of the program.
 * @return Query configuration object for the program detail.
 */
export const programDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['programs', id],
        queryFn: () => programsApi.get(id),
    })
