import { createFileRoute, redirect } from '@tanstack/react-router'
import { Suspense } from 'react'
import { ErrorBoundary } from 'react-error-boundary'
import type { FallbackProps } from 'react-error-boundary'
import { ROUTES } from '@/app/constants'
import { ClientLayout } from '@/features/auth/components/ClientLayout'
import { Spinner } from '@/shared/components/ui/spinner'

function PageLoader() {
    return (
        <div className="flex items-center justify-center min-h-dvh bg-grey-950">
            <Spinner className="size-6 text-grey-600" />
        </div>
    )
}

function PageError({ error }: FallbackProps) {
    const message = error instanceof Error ? error.message : 'An unexpected error occurred.'
    return (
        <div className="flex flex-col items-center justify-center min-h-dvh bg-grey-950 gap-3">
            <p className="text-sm font-medium text-grey-200">Something went wrong</p>
            <p className="text-xs text-grey-500 max-w-sm text-center">{message}</p>
        </div>
    )
}

export const Route = createFileRoute('/_auth/client/_layout')({
    beforeLoad: ({ context }) => {
        if (context.isTrainer) {
            throw redirect({ to: ROUTES.trainer.dashboard })
        }
    },
    component: () => (
        <ErrorBoundary FallbackComponent={PageError}>
            <Suspense fallback={<PageLoader />}>
                <ClientLayout />
            </Suspense>
        </ErrorBoundary>
    ),
})
