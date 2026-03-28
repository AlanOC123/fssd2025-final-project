import { create } from 'zustand'
import { authApi } from '@/features/auth/api'
import type { AuthUser, AuthState, LoginCredentials } from '@/features/auth/types'
import { tryCatch } from '@/shared/utils/tryCatch'

/**
 * Interface representing the authentication store state and actions.
 */
interface AuthStore extends AuthState {
    /**
     * Authenticates a user and updates the store with profile data.
     *
     * @param credentials The user's login credentials.
     * @throws The error encountered during the login process.
     * @return A promise that resolves when the login process is complete.
     */
    login: (credentials: LoginCredentials) => Promise<void>

    /**
     * Logs out the current user and clears the store.
     *
     * @return A promise that resolves when the logout process is complete.
     */
    logout: () => Promise<void>

    /**
     * Fetches the current user's profile and updates the store.
     *
     * @return A promise that resolves when the user profile is fetched.
     */
    fetchUser: () => Promise<void>

    /**
     * Manually updates the user profile in the store.
     *
     * @param user The user object or null to clear the session.
     */
    setUser: (user: AuthUser | null) => void
}

/**
 * Zustand store for managing global authentication state.
 *
 * This store handles user data, loading states, and authentication status,
 * providing actions for login, logout, and profile synchronization.
 */
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
            return
        }

        set({ user, isAuthenticated: true, isLoading: false })
    },

    setUser: (user) => {
        set({ user, isAuthenticated: user !== null })
    },
}))
