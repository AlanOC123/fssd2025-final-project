import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { TrainerProfile, ClientProfile } from '@/features/auth/types'

/**
 * Payload for updating a trainer's professional profile details.
 */
export interface UpdateTrainerProfilePayload {
    /** Optional company or organization name. */
    company?: string
    /** Optional professional website URL. */
    website?: string
    /** List of UUIDs representing the goals the trainer accepts. */
    accepted_goal_ids?: string[]
    /** List of UUIDs representing the fitness levels the trainer works with. */
    accepted_level_ids?: string[]
}

/** Cache key for trainer profile queries. */
export const TRAINER_PROFILE_QUERY_KEY = ['trainer', 'profile'] as const
/** Cache key for client profile queries. */
export const CLIENT_PROFILE_QUERY_KEY = ['client', 'profile'] as const

/**
 * API methods for managing trainer profile data.
 */
export const trainerProfileApi = {
    /**
     * Retrieves the profile data for the currently authenticated trainer.
     *
     * @return A promise resolving to the trainer's profile data.
     */
    get: () => api.get<TrainerProfile>('/users/trainer-profile/me/'),

    /**
     * Updates the trainer's profile information.
     *
     * @param payload The fields to be updated.
     * @return A promise resolving to the updated trainer profile.
     */
    update: (payload: UpdateTrainerProfilePayload) =>
        api.patch<TrainerProfile>('/users/trainer-profile/me/update/', payload),

    /**
     * Uploads and updates the trainer's professional logo.
     *
     * @param file The image file to be used as the logo.
     * @return A promise resolving to the updated trainer profile.
     */
    updateLogo: (file: File): Promise<TrainerProfile> => {
        const form = new FormData()
        form.append('logo', file)
        return api.patch<TrainerProfile>('/users/trainer-profile/me/update/', form)
    },
}

/**
 * API methods for managing client profile data.
 */
export const clientProfileApi = {
    /**
     * Retrieves the profile data for the currently authenticated client.
     *
     * @return A promise resolving to the client's profile data.
     */
    get: () => api.get<ClientProfile>('/users/client-profile/me/'),

    /**
     * Updates the client's goal or fitness level.
     *
     * @param payload Object containing the optional goal or level IDs.
     * @return A promise resolving to the updated client profile.
     */
    update: (payload: { goal_id?: string | null; level_id?: string | null }) =>
        api.patch<ClientProfile>('/users/client-profile/me/update/', payload),

    /**
     * Uploads and updates the client's profile avatar.
     *
     * @param file The image file to be used as the avatar.
     * @return A promise resolving to the updated client profile.
     */
    updateAvatar: (file: File): Promise<ClientProfile> => {
        const form = new FormData()
        form.append('avatar', file)
        return api.patch<ClientProfile>('/users/client-profile/me/update/', form)
    },
}

/**
 * Creates configuration options for fetching the trainer's profile via TanStack Query.
 *
 * @return Configuration object for the trainer profile query.
 */
export const trainerProfileQueryOptions = () =>
    queryOptions({
        queryKey: TRAINER_PROFILE_QUERY_KEY,
        queryFn: trainerProfileApi.get,
    })
