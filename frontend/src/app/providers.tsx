import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import { isApiError } from '@/shared/utils/errors'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 5 * 60,
            retry: (failureCount, error) => {
                if (isApiError(error) && error.status >= 400 && error.status <= 500) {
                    return false
                }

                return failureCount > 2
            },
        },
    },
})

export function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
            {import.meta.env.DEV && <ReactQueryDevtools buttonPosition="bottom-left" />}
        </QueryClientProvider>
    )
}
