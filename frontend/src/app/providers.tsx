import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import { isApiError } from '@/shared/utils/errors'
import { useAuthStore } from '@/features/auth'
import { useAuthQuery } from '@/features/auth/hooks/useAuthQuery'
import { GoeyToaster } from '@/shared/components/ui/goey-toaster'

/**
 * Global QueryClient configuration.
 * Sets default stale time to 5 minutes and implements a custom retry strategy
 * that prevents retrying on client-side (4xx) errors.
 */
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 1000 * 5 * 60,
            retry: (failureCount, error) => {
                if (isApiError(error) && error.status >= 400 && error.status < 500) {
                    return false
                }

                return failureCount < 2
            },
        },
    },
})

/**
 * Component responsible for managing the application's routing and auth context.
 * It waits for the initial authentication check before rendering the router.
 * * @returns {JSX.Element} The initialized router provider or a loading spinner.
 */
function InnerApp() {
    const user = useAuthStore((s) => s.user)
    const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
    const { isLoading } = useAuthQuery()

    if (isLoading) {
        return (
            <div className="min-h-dvh flex items-center justify-center bg-grey-950">
                <div className="size-6 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
            </div>
        )
    }

    return (
        <RouterProvider
            router={router}
            context={{
                isAuthenticated,
                isTrainer: user?.is_trainer,
                isClient: user?.is_client,
                isAdmin: user?.role === 'admin',
                queryClient,
            }}
        />
    )
}

/**
 * Main entry point for the React application.
 * Wraps the application with global providers including React Query and the Toaster.
 * * @returns {JSX.Element} The root application component.
 */
export function App() {
    // Determine development environment using a build-compatible check.
    const isDev = !!import.meta.env.DEV

    return (
        <QueryClientProvider client={queryClient}>
            <GoeyToaster
                position={'top-center'}
                offset={'24px'}
                theme={'dark'}
                spring={true}
                bounce={0.5}
            />
            <InnerApp />
            {isDev && <ReactQueryDevtools buttonPosition="bottom-right" />}
        </QueryClientProvider>
    )
}
