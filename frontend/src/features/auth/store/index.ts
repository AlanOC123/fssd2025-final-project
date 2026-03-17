import { create } from 'zustand'
import { authApi } from '@/features/auth/api'
import type { AuthUser, AuthState, LoginCredentials } from '@/features/auth/types'
import { tryCatch } from '@/shared/utils/tryCatch'

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

        const { data: user, error } = await tryCatch(authApi.login(credentials))

        if (error) {
            set({ isLoading: false })
            throw error
        }

        set({ user, isAuthenticated: true, isLoading: false })
    },

    logout: async () => {
        set({ isLoading: true })

        await tryCatch(authApi.logout()).finally(() =>
            set({ user: null, isAuthenticated: false, isLoading: false }),
        )
    },

    fetchUser: async () => {
        set({ isLoading: true })

        const { data: user, error } = await tryCatch(authApi.getUser())

        if (error) {
            set({ user: null, isAuthenticated: false, isLoading: false })
        }

        set({ user, isAuthenticated: true, isLoading: false })
    },

    setUser: (user) => {
        set({ user, isAuthenticated: user !== null })
    },
}))
