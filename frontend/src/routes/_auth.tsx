import { ROUTES } from "@/app/constants";
import { createFileRoute, redirect, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute('/_auth')({
    beforeLoad: ({ context }) => {
        if (!context.isAuthenticated) {
            throw redirect({ to: ROUTES.login })
        }
    },
    component: Outlet
})
