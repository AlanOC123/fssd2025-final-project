import { useQuery } from '@tanstack/react-query'
import { authApi } from '../api'
import { useAuthStore } from '../store'
import { tryCatch } from '@/shared/utils/tryCatch'
import { isApiError } from '@/shared/utils/errors'

export const AUTH_QUERY_KEY = ['auth', 'user'] as const

export function useAuthQuery() {
    const setUser = useAuthStore((s) => s.setUser)

    return useQuery({
        queryKey: AUTH_QUERY_KEY,
        queryFn: async () => {
            const { data: user, error } = await tryCatch(authApi.getUser())

            if (error) {
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
        staleTime: Infinity
    })
}
