import { api } from '@/shared/api/client'
import type { AuthUser, LoginCredentials } from '../types'

export const authApi = {
    login: (credentials: LoginCredentials) => api.post<AuthUser>('/auth/login/', credentials),

    logout: () => api.post<void>('/auth/login/'),

    getUser: () => api.get<AuthUser>('/auth/user/'),
}
