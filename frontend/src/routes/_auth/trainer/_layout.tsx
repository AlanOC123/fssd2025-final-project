import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import { ROUTES } from '@/app/constants'
import { TrainerLayout } from '@/features/auth/components/TrainerLayout'
import { Spinner } from '@/shared/components/ui/spinner'
import type { FallbackProps } from 'react-error-boundary'

function PageLoader() {
    return (
        <div className="flex items-center justify-center min-h-dvh w-full bg-grey-950">
            <Spinner className="size-6 text-grey-600" />
        </div>
    )
}

function PageError({ error }: FallbackProps) {
    const message = error instanceof Error ? error.message : 'An unexpected error has occured.'
    return (
        <div className="flex flex-col items-center justify-center min-h-dvh bg-grey-950 gap-3">
            <p className="text-sm font-medium text-grey-200">Something went wrong</p>
            <p className="text-xs text-grey-500 max-w-sm text-center">{message}</p>
        </div>
    )
}

export const Route = createFileRoute('/_auth/trainer/_layout')({
    beforeLoad: ({ context }) => {
        if (context.isClient) {
            throw redirect({ to: ROUTES.client.dashboard })
        }
    },

    component: () => (
        <ErrorBoundary FallbackComponent={PageError}>
            <Suspense fallback={<PageLoader />}>
                <TrainerLayout />
            </Suspense>
        </ErrorBoundary>
    ),
})
