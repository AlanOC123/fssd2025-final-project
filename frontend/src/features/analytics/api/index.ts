import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { LoadHistoryEntry } from '../types'

export const analyticsApi = {
    loadHistory: (programId: string, exerciseId: string) =>
        api.get<LoadHistoryEntry[]>(
            `/analytics/programs/${programId}/exercises/${exerciseId}/load-history/`,
        ),
}

export const loadHistoryQueryOptions = (programId: string, exerciseId: string) =>
    queryOptions({
        queryKey: ['analytics', 'load-history', programId, exerciseId],
        queryFn: () => analyticsApi.loadHistory(programId, exerciseId),
        select: (data) => (Array.isArray(data) ? data : []),
    })
