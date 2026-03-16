import axios from 'axios'

export interface ApiError {
    status: number
    message: string
    detail?: string | Record<string, string[]>
}

export function normaliseError(error: unknown): ApiError {
    if (axios.isAxiosError(error)) {
        const status = error.response?.status ?? 0
        const data = error.response?.data

        return {
            status,
            message: error.message,
            detail: data?.detail ?? data,
        }
    }

    return {
        status: 0,
        message: 'An unexpected error occurred',
    }
}

export function isApiError(error: unknown): error is ApiError {
    return typeof error === 'object' && error !== null && 'status' in error && 'message' in error
}
