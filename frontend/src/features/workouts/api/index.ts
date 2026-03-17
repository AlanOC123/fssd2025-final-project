import { api } from "@/shared/api/client";
import { queryOptions } from "@tanstack/react-query";
import type { PaginatedResponse } from "@/shared/types/base";
import type { WorkoutListItem, WorkoutDetail } from "../types";

export interface WorkoutsParams {
    program_phase?: string
    planned_date?: string
}

const WORKOUT_QUERY_KEY = (params?: WorkoutsParams) => ['workouts', params ?? {}] as const

export const workoutsApi = {
    list: (params? : WorkoutsParams) => api.get<PaginatedResponse<WorkoutListItem>>('/workouts/workouts/', { params }),

    get: (id: string) => api.get<WorkoutDetail>(`/workouts/workouts/${id}/`)
}

export const workoutsQueryOptions = (params?: WorkoutsParams) =>
    queryOptions({
        queryKey: WORKOUT_QUERY_KEY(params),
        queryFn: () => workoutsApi.list(params)
    })
