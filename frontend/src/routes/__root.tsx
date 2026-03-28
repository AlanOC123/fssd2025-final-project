import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import type { RouteContext } from '@/app/router'

/**
 * The root route configuration for the application.
 * Utilizes `createRootRouteWithContext` to enforce type safety for the
 * global context (auth state, query client, etc.) shared across all routes.
 */
export const Route = createRootRouteWithContext<RouteContext>()({
    /**
     * The root layout component.
     * Renders the main outlet for child routes and conditionally includes
     * the TanStack Router devtools in development environments.
     * * @returns {JSX.Element} The base application layout.
     */
    component: () => {
        // Environment check using process.env as a fallback for environments
        // where import.meta is not available.
        const isDev = !!import.meta.env.DEV

        return (
            <>
                <Outlet />
                {isDev && <TanStackRouterDevtools position="bottom-right" />}
            </>
        )
    },
})
