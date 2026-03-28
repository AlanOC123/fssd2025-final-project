import { useAuthStore } from '@/features/auth/store'
import type { AuthUser } from '@/features/auth/types'

/**
 * Custom hook for accessing authentication state and actions.
 * * Provides a simplified interface to the AuthStore, including user profile
 * information, authentication status, and helper methods for role-based
 * logic (Trainer/Client).
 * * Returns:
 * An object containing:
 * - user: Current authenticated user object or null.
 * - isAuthenticated: Boolean indicating if a user is logged in.
 * - isLoading: Boolean indicating if the auth state is being fetched.
 * - login/logout/setUser: Action functions to modify auth state.
 * - isTrainer/isClient: Derived booleans for role-based UI logic.
 * - asTrainer: Function to retrieve trainer-specific profile data.
 */
export function useAuth() {
    const user = useAuthStore((s) => s.user)
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
    const isLoading = useAuthStore((s) => s.isLoading)

    const login = useAuthStore((s) => s.login)
    const logout = useAuthStore((s) => s.logout)
    const setUser = useAuthStore((s) => s.setUser)

    const isTrainer = user?.is_trainer ?? false
    const isClient = user?.is_client ?? false

    /**
     * Type-safe accessor for the user's Trainer profile.
     * * Returns:
     * The trainer profile if the user is a trainer, otherwise null.
     */
    function asTrainer(): Extract<AuthUser['profile'], { accepted_goals: unknown } | null> {
        return isTrainer
            ? ((user?.profile as Extract<AuthUser['profile'], { accepted_goals: unknown }>) ?? null)
            : null
    }

    return {
        user,
        isAuthenticated,
        isLoading,
        login,
        logout,
        setUser,
        isTrainer,
        isClient,
        asTrainer,
    }
}
