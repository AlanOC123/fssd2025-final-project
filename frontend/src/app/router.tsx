import { createRouter } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'
import { QueryClient } from '@tanstack/react-query'

/**
 * Defines the shared context available to all routes within the application.
 * This context is used for type-safe access to authentication state,
 * user roles, and the query client instance.
 */
export interface RouteContext {
    isAuthenticated: boolean
    isTrainer: boolean
    isClient: boolean
    isAdmin: boolean
    queryClient: QueryClient
}

/**
 * The global router instance configured with the generated route tree.
 * Includes default settings for preloading, scroll restoration, and
 * initial context state.
 */
export const router = createRouter({
    routeTree,
    context: {
        isAuthenticated: false,
        isTrainer: false,
        isClient: false,
        isAdmin: false,
        queryClient: undefined!,
    } satisfies RouteContext,
    defaultPreload: 'intent',
    defaultPreloadDelay: 100,
    scrollRestoration: true,
})

/**
 * Registers the router instance for maximum type safety across the application.
 */
declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}
