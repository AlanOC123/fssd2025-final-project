import { gooeyToast } from '@/shared/components/ui/goey-toaster'
import type { GooeyToastOptions, GooeyPromiseData } from '@/shared/components/ui/goey-toaster'
import { isApiError } from './errors'

export const toast = {
    success: (title: string, options?: GooeyToastOptions) => gooeyToast.success(title, options),

    error: (title: string, options?: GooeyToastOptions) => gooeyToast.error(title, options),

    warning: (title: string, options?: GooeyToastOptions) => gooeyToast.warning(title, options),

    info: (title: string, options?: GooeyToastOptions) => gooeyToast.info(title, options),

    promise: <T>(promise: Promise<T>, data: GooeyPromiseData<T>) =>
        gooeyToast.promise(promise, data),

    dismiss: gooeyToast.dismiss,
}


export function toastApiError(
    error: unknown,
    errorTitle = 'Request failed',
    fallbackDesc = 'Something went wrong',
) {
    if (!error) return

    if (!isApiError(error)) {
        toast.error(errorTitle, { description: fallbackDesc })
        return
    }

    const { status, message, detail } = error

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

    if ('non_field_errors' in detail) {
        const nfe = detail.non_field_errors
        if (Array.isArray(nfe) && nfe.length > 0) {
            toast.error(errorTitle, { description: nfe[0] })
            return
        }
    }

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
