import { createRouter } from '@tanstack/react-router'
import { routeTree } from '@/routeTree.gen'

export interface RouteContext {
    isAuthenticated: boolean
    role: 'trainer' | 'client' | 'admin' | null
}

export const router = createRouter({
    routeTree,
    context: {
        isAuthenticated: false,
        role: null,
    } satisfies RouteContext,
    defaultPreload: 'intent',
    defaultPreloadDelay: 100,
    scrollResortation: true,
})

declare module '@tanstack/react-router' {
    interface Register {
        router: typeof router
    }
}
