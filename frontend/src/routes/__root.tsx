import { createRootRouteWithContext, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'
import type { RouteContext } from '@/app/router'

export const Route = createRootRouteWithContext<RouteContext>()({
    component: () => {
        return (
            <>
                <Outlet />
                {import.meta.env.DEV && <TanStackRouterDevtools position="bottom-right" />}
            </>
        )
    },
})
