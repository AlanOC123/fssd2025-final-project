import { api } from '@/shared/api/client'
import { queryOptions } from '@tanstack/react-query'
import type { TrainerProfile, ClientProfile } from '@/features/auth/types'

export interface UpdateTrainerProfilePayload {
    company?: string
    website?: string
    accepted_goal_ids?: string[]
    accepted_level_ids?: string[]
}

export const TRAINER_PROFILE_QUERY_KEY = ['trainer', 'profile'] as const
export const CLIENT_PROFILE_QUERY_KEY = ['client', 'profile'] as const

export const trainerProfileApi = {
    get: () => api.get<TrainerProfile>('/users/trainer-profile/me/'),
    update: (payload: UpdateTrainerProfilePayload) =>
        api.patch<TrainerProfile>('/users/trainer-profile/me/update/', payload),

    updateLogo: (file: File): Promise<TrainerProfile> => {
        const form = new FormData()
        form.append('logo', file)
        return api.patch<TrainerProfile>('/users/trainer-profile/me/update/', form)
    },
}

export const clientProfileApi = {
    get: () => api.get<ClientProfile>('/users/client-profile/me/'),

    update: (payload: { goal_id?: string | null; level_id?: string | null }) =>
        api.patch<ClientProfile>('/users/client-profile/me/update/', payload),

    updateAvatar: (file: File): Promise<ClientProfile> => {
        const form = new FormData()
        form.append('avatar', file)
        return api.patch<ClientProfile>('/users/client-profile/me/update/', form)
    },
}


export const trainerProfileQueryOptions = () =>
    queryOptions({
        queryKey: TRAINER_PROFILE_QUERY_KEY,
        queryFn: trainerProfileApi.get,
    })
