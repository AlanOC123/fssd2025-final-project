import { api } from '@/shared/api/client'
import type { AuthUser, LoginResponse, LoginCredentials } from '../types'

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<AuthUser> => {
        const response = await api.post<LoginResponse>('/auth/login/', credentials);
        return response.user
    },

    logout: () => api.post<void>('/auth/logout/'),

    getUser: () => api.get<AuthUser>('/auth/user/'),
}
