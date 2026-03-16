import { create } from 'zustand'
import { authApi } from '@/features/auth/api'
import type { AuthUser, AuthState, LoginCredentials } from '@/features/auth/types'

interface AuthStore extends AuthState {
    login: (credentials: LoginCredentials) => Promise<void>
    logout: () => Promise<void>
    fetchUser: () => Promise<void>
    setUser: (user: AuthUser | null) => void
}

export const useAuthStore = create<AuthStore>((set) => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,

    login: async (credentials: LoginCredentials) => {
        set({ isLoading: true })

        try {
            const user = await authApi.login(credentials)
            set({ user, isAuthenticated: true, isLoading: false })
        } catch (error) {
            set({ isLoading: false })
            throw error
        }
    },

    logout: async () => {
        set({ isLoading: true })

        try {
            await authApi.logout()
        } finally {
            set({ user: null, isAuthenticated: false, isLoading: false })
        }
    },

    fetchUser: async () => {
        set({ isLoading: true })

        try {
            const user = await authApi.getUser()
            set({ user, isAuthenticated: true, isLoading: false })
        } catch {
            set({ user: null, isAuthenticated: false, isLoading: false })
        }
    },

    setUser: async (user) => {
        set({ user, isAuthenticated: user !== null })
    },
}))
