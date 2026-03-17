import { createRouter } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'
import { QueryClient } from '@tanstack/react-query'

export interface RouteContext {
    isAuthenticated: boolean
    isTrainer: boolean
    isClient: boolean
    isAdmin: boolean
    queryClient: QueryClient
}

export const router = createRouter({
    routeTree,
    context: {
        isAuthenticated: false,
        isTrainer: false,
        isClient: false,
        isAdmin: false,
        queryClient: undefined!
    } satisfies RouteContext,
    defaultPreload: 'intent',
    defaultPreloadDelay: 100,
    scrollRestoration: true,
})

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}
