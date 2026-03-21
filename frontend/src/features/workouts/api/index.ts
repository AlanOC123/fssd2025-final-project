import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { PaginatedResponse } from '@/shared/types/base'
import type {
    WorkoutListItem,
    WorkoutDetail,
    CreateWorkoutExercisePayload,
    CreateWorkoutSetPayload,
    CreateWorkoutPayload,
} from '../types'

export interface WorkoutsParams {
    program_phase?: string
    planned_date?: string
}

export const WORKOUT_QUERY_KEY = (params?: WorkoutsParams) => ['workouts', params ?? {}] as const

export const workoutsApi = {
    list: (params?: WorkoutsParams) =>
        api.get<PaginatedResponse<WorkoutListItem>>('/workouts/workouts/', { params }),

    get: (id: string) => api.get<WorkoutDetail>(`/workouts/workouts/${id}/`),

    create: (payload: CreateWorkoutPayload) =>
        api.post<WorkoutDetail>('/workouts/workouts/', payload),

    delete: (id: string) => api.delete<void>(`/workouts/workouts/${id}/`),

    addExercise: (payload: CreateWorkoutExercisePayload) =>
        api.post<WorkoutDetail>('/workouts/workout-exercises/', payload),

    removeExercise: (id: string) => api.delete<void>(`/workouts/workout-exercises/${id}/`),

    addSet: (payload: CreateWorkoutSetPayload) =>
        api.post<WorkoutDetail>('/workouts/workout-sets/', payload),

    removeSet: (id: string) => api.delete<void>(`/workouts/workout-sets/${id}/`),
}

export const workoutsQueryOptions = (params?: WorkoutsParams) =>
    queryOptions({
        queryKey: WORKOUT_QUERY_KEY(params),
        queryFn: () => workoutsApi.list(params),
    })

export const workoutDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['workouts', id],
        queryFn: () => workoutsApi.get(id),
    })
