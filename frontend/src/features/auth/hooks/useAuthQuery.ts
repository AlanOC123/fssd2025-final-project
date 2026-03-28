import { useQuery } from '@tanstack/react-query'
import { authApi } from '../api'
import { useAuthStore } from '../store'
import { tryCatch } from '@/shared/utils/tryCatch'
import { isApiError } from '@/shared/utils/errors'

/**
 * Cache key for the authentication user query.
 */
export const AUTH_QUERY_KEY = ['auth', 'user'] as const

/**
 * Custom hook to fetch and manage the authenticated user's state.
 *
 * This hook synchronizes the API user state with the local `useAuthStore`.
 * If a 401 Unauthorized error is encountered, it clears the local session.
 *
 * @return The TanStack Query result containing the current AuthUser or null.
 */
export function useAuthQuery() {
    const setUser = useAuthStore((s) => s.setUser)

    return useQuery({
        queryKey: AUTH_QUERY_KEY,
        queryFn: async () => {
            const { data: user, error } = await tryCatch(authApi.getUser())

            if (error) {
                // Handle session expiration by checking for 401 status.
                const isUnauthorised = isApiError(error) && error.status === 401

                if (isUnauthorised) {
                    setUser(null)
                }
                return null
            }

            setUser(user)
            return user
        },
        retry: false,
        staleTime: Infinity,
    })
}
