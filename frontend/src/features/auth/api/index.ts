import { api } from '@/shared/api/client'
import type { AuthUser, LoginResponse, LoginCredentials } from '../types'

export interface UpdateUserPayload {
    first_name?: string
    last_name?: string
}

export interface RegisterPayload {
    email: string
    password1: string
    password2: string
    first_name: string
    last_name: string
    role: 'trainer' | 'client'
}

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<AuthUser> => {
        const response = await api.post<LoginResponse>('/auth/login/', credentials)
        return response.user
    },

    logout: () => api.post<void>('/auth/logout/'),

    getUser: () => api.get<AuthUser>('/auth/user/'),

    updateUser: (payload: UpdateUserPayload): Promise<AuthUser> =>
        api.patch<AuthUser>('/auth/user/', payload),

    updateAvatar: (file: File): Promise<AuthUser> => {
        const form = new FormData()
        form.append('avatar', file)
        return api.patch<AuthUser>('/auth/user/', form, {
            headers: { 'Content-Type': 'multipart/form-data' },
        })
    },

    register: async (payload: RegisterPayload): Promise<AuthUser> => {
        const response = await api.post<LoginResponse>('/auth/registration/', payload)
        return response.user
    },

    forgotPassword: (email: string) => api.post<void>('/auth/password/reset/', { email }),

    resetPasswordConfirm: (payload: {
        uid: string
        token: string
        new_password1: string
        new_password2: string
    }) => api.post<void>('/auth/password/reset/confirm/', payload),
}
