import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import type { FallbackProps } from 'react-error-boundary'
import { ROUTES } from '@/app/constants'
import { ClientLayout } from '@/features/auth/components/ClientLayout'
import { Spinner } from '@/shared/components/ui/spinner'

/**
 * Renders a full-screen loading state with a centered spinner.
 *
 * @return {JSX.Element} The loading spinner component.
 */
function PageLoader() {
    return (
        <div className="flex items-center justify-center min-h-dvh bg-grey-950">
            <Spinner className="size-6 text-grey-600" />
        </div>
    )
}

/**
 * Fallback component for the route's error boundary.
 *
 * @param {FallbackProps} props The props provided by react-error-boundary.
 * @return {JSX.Element} A centered error message display.
 */
function PageError({ error }: FallbackProps) {
    const message = error instanceof Error ? error.message : 'An unexpected error occurred.'
    return (
        <div className="flex flex-col items-center justify-center min-h-dvh bg-grey-950 gap-3">
            <p className="text-sm font-medium text-grey-200">Something went wrong</p>
            <p className="text-xs text-grey-500 max-w-sm text-center">{message}</p>
        </div>
    )
}

/**
 * Route definition for the client-specific layout.
 *
 * This route enforces role-based access control and wraps the client
 * dashboard layout with necessary error boundaries and suspense boundaries.
 */
export const Route = createFileRoute('/_auth/client/_layout')({
    /**
     * Validates user role before loading the client layout.
     *
     * @param {{
     * context: {
     * isTrainer: boolean;
     * };
     * }} options The route transition options containing authentication context.
     * @throws {ReturnType<typeof redirect>} Redirects to the trainer dashboard
     * if the user is a trainer.
     */
    beforeLoad: ({ context }) => {
        if (context.isTrainer) {
            throw redirect({ to: ROUTES.trainer.dashboard })
        }
    },
    /**
     * Composition of the client layout with error handling and async boundaries.
     *
     * @return {JSX.Element} The wrapped client layout.
     */
    component: () => (
        <ErrorBoundary FallbackComponent={PageError}>
            <Suspense fallback={<PageLoader />}>
                <ClientLayout />
            </Suspense>
        </ErrorBoundary>
    ),
})
