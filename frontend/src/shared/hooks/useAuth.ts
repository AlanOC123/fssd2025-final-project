import { useAuthStore } from '@/features/auth/store'
import type { AuthUser } from '@/features/auth/types'

export function useAuth() {
    const user = useAuthStore((s) => s.user)
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
    const isLoading = useAuthStore((s) => s.isLoading)

    const login = useAuthStore((s) => s.login)
    const logout = useAuthStore((s) => s.logout)
    const setUser = useAuthStore((s) => s.setUser)

    const isTrainer = user?.is_trainer ?? false
    const isClient = user?.is_client ?? false

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
