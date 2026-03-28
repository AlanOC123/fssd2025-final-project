import { gooeyToast } from '@/shared/components/ui/goey-toaster'
import type { GooeyToastOptions, GooeyPromiseData } from '@/shared/components/ui/goey-toaster'
import { isApiError } from './errors'

/**
 * @fileoverview Utility for displaying various types of toast notifications.
 * Wraps the underlying toast provider to provide a consistent interface
 * and specialized handling for API errors.
 */

/**
 * Global toast controller for standard notification types.
 */
export const toast = {
    success: (title: string, options?: GooeyToastOptions) => gooeyToast.success(title, options),

    error: (title: string, options?: GooeyToastOptions) => gooeyToast.error(title, options),

    warning: (title: string, options?: GooeyToastOptions) => gooeyToast.warning(title, options),

    info: (title: string, options?: GooeyToastOptions) => gooeyToast.info(title, options),

    promise: <T>(promise: Promise<T>, data: GooeyPromiseData<T>) =>
        gooeyToast.promise(promise, data),

    dismiss: gooeyToast.dismiss,
}

/**
 * Parses an unknown error and displays the most relevant message via an error toast.
 *
 * This function traverses standardized ApiError structures to find deep field
 * errors or non-field errors, ensuring the user sees specific feedback if available.
 *
 * Args:
 * error: The caught error to process.
 * errorTitle: Header text for the toast notification.
 * fallbackDesc: Message to show if no specific error details can be extracted.
 */
export function toastApiError(
    error: unknown,
    errorTitle = 'Request failed',
    fallbackDesc = 'Something went wrong',
) {
    if (!error) return

    // Fallback if the error doesn't follow the application's API error format.
    if (!isApiError(error)) {
        toast.error(errorTitle, { description: fallbackDesc })
        return
    }

    const { status, message, detail } = error

    // Display the top-level message if the error is not a client-side or server failure.
    if (!status || status < 400) {
        toast.error(errorTitle, { description: message })
        return
    }

    if (!detail) {
        toast.error(errorTitle, { description: message })
        return
    }

    if (typeof detail === 'string') {
        toast.error(errorTitle, { description: detail })
        return
    }

    /**
     * Handle Django/Rest Framework style 'non_field_errors' specifically.
     */
    if ('non_field_errors' in detail) {
        const nfe = detail.non_field_errors
        if (Array.isArray(nfe) && nfe.length > 0) {
            toast.error(errorTitle, { description: nfe[0] })
            return
        }
    }

    /**
     * Fallback to displaying the first available validation error from any field.
     */
    const firstField = Object.keys(detail)[0]
    if (firstField) {
        const fieldErrors = detail[firstField]
        if (Array.isArray(fieldErrors) && fieldErrors.length > 0) {
            const label = firstField === 'non_field_errors' ? '' : `${firstField}: `
            toast.error(errorTitle, { description: `${label}${fieldErrors[0]}` })
            return
        }
    }

    toast.error(errorTitle, { description: message })
}
