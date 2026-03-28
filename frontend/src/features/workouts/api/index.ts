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

/**
 * Filter parameters for querying workouts.
 */
export interface WorkoutsParams {
    /** Optional ID of the program phase to filter workouts. */
    program_phase?: string
    /** Optional date string (ISO format) to filter workouts by planned date. */
    planned_date?: string
}

/**
 * Generates a consistent query key for workout-related queries.
 *
 * @param params Optional filters applied to the query.
 * @return A read-only array used as the query key.
 */
export const WORKOUT_QUERY_KEY = (params?: WorkoutsParams) => ['workouts', params ?? {}] as const

/**
 * API methods for interacting with workout resources.
 */
export const workoutsApi = {
    /**
     * Fetches a paginated list of workouts.
     *
     * @param params Optional filtering parameters.
     * @return A promise resolving to a paginated response of workout items.
     */
    list: (params?: WorkoutsParams) =>
        api.get<PaginatedResponse<WorkoutListItem>>('/workouts/workouts/', { params }),

    /**
     * Retrieves detailed information for a specific workout.
     *
     * @param id The unique identifier of the workout.
     * @return A promise resolving to the detailed workout data.
     */
    get: (id: string) => api.get<WorkoutDetail>(`/workouts/workouts/${id}/`),

    /**
     * Creates a new workout record.
     *
     * @param payload The data required to create a workout.
     * @return A promise resolving to the created workout details.
     */
    create: (payload: CreateWorkoutPayload) =>
        api.post<WorkoutDetail>('/workouts/workouts/', payload),

    /**
     * Deletes a specific workout record.
     *
     * @param id The unique identifier of the workout to delete.
     * @return A promise resolving when the deletion is complete.
     */
    delete: (id: string) => api.delete<void>(`/workouts/workouts/${id}/`),

    /**
     * Adds a new exercise to an existing workout.
     *
     * @param payload The data required to link an exercise to a workout.
     * @return A promise resolving to the updated workout details.
     */
    addExercise: (payload: CreateWorkoutExercisePayload) =>
        api.post<WorkoutDetail>('/workouts/workout-exercises/', payload),

    /**
     * Removes an exercise from a workout.
     *
     * @param id The unique identifier of the workout-exercise relation.
     * @return A promise resolving when the exercise is removed.
     */
    removeExercise: (id: string) => api.delete<void>(`/workouts/workout-exercises/${id}/`),

    /**
     * Adds a performance set to a workout exercise.
     *
     * @param payload The data required to create a new set.
     * @return A promise resolving to the updated workout details.
     */
    addSet: (payload: CreateWorkoutSetPayload) =>
        api.post<WorkoutDetail>('/workouts/workout-sets/', payload),

    /**
     * Removes a specific set from a workout exercise.
     *
     * @param id The unique identifier of the set to remove.
     * @return A promise resolving when the set is removed.
     */
    removeSet: (id: string) => api.delete<void>(`/workouts/workout-sets/${id}/`),
}

/**
 * Creates query options for fetching a list of workouts.
 *
 * @param params Optional filtering parameters for the list.
 * @return Configuration for TanStack Query list fetching.
 */
export const workoutsQueryOptions = (params?: WorkoutsParams) =>
    queryOptions({
        queryKey: WORKOUT_QUERY_KEY(params),
        queryFn: () => workoutsApi.list(params),
    })

/**
 * Creates query options for fetching a single workout's details.
 *
 * @param id The unique identifier of the workout.
 * @return Configuration for TanStack Query detail fetching.
 */
export const workoutDetailQueryOptions = (id: string) =>
    queryOptions({
        queryKey: ['workouts', id],
        queryFn: () => workoutsApi.get(id),
    })
