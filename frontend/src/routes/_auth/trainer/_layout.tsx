import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { ROUTES } from '@/app/constants'
import { TrainerLayout } from '@/features/auth/components/TrainerLayout'
import { Spinner } from '@/shared/components/ui/spinner'
import type { FallbackProps } from 'react-error-boundary'

/**
 * Renders a full-screen loading state with a centered spinner.
 *
 * @return {JSX.Element} A div containing a centered spinner component.
 */
function PageLoader() {
    return (
        <div className="flex items-center justify-center min-h-dvh w-full bg-grey-950">
            <Spinner className="size-6 text-grey-600" />
        </div>
    )
}

/**
 * Fallback component for the route's error boundary.
 *
 * @param {FallbackProps} props The props provided by react-error-boundary.
 * @return {JSX.Element} A centered error message display with error details.
 */
function PageError({ error }: FallbackProps) {
    const message = error instanceof Error ? error.message : 'An unexpected error has occured.'
    return (
        <div className="flex flex-col items-center justify-center min-h-dvh bg-grey-950 gap-3">
            <p className="text-sm font-medium text-grey-200">Something went wrong</p>
            <p className="text-xs text-grey-500 max-w-sm text-center">{message}</p>
        </div>
    )
}

/**
 * Route definition for the trainer-specific layout.
 *
 * This route enforces role-based access control, ensuring client users are
 * redirected to their appropriate dashboard if they attempt to access
 * trainer-only layout areas.
 */
export const Route = createFileRoute('/_auth/trainer/_layout')({
    /**
     * Validates user role before loading the trainer layout.
     *
     * @param {{
     * context: {
     * isClient: boolean;
     * };
     * }} options The route transition options containing authentication context.
     * @throws {ReturnType<typeof redirect>} Redirects client users to the client
     * dashboard.
     */
    beforeLoad: ({ context }) => {
        if (context.isClient) {
            throw redirect({ to: ROUTES.client.dashboard })
        }
    },

    /**
     * Composition of the trainer layout wrapped in error handling and
     * loading states.
     *
     * @return {JSX.Element} The trainer layout wrapped in ErrorBoundary and Suspense.
     */
    component: () => (
        <ErrorBoundary FallbackComponent={PageError}>
            <Suspense fallback={<PageLoader />}>
                <TrainerLayout />
            </Suspense>
        </ErrorBoundary>
    ),
})
