import axios, {
    type AxiosInstance,
    type AxiosRequestConfig,
    type AxiosResponse,
    type InternalAxiosRequestConfig,
} from 'axios'

import { normaliseError, type ApiError } from '@/shared/utils/errors'

// Types
export type { ApiError }
interface RetryableRequest extends InternalAxiosRequestConfig {
    _retry?: boolean
}

// Base Axios Client
const client: AxiosInstance = axios.create({
    baseURL: '/api/v1',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
})

// Request interceptor — remove Content-Type for FormData so Axios sets it
// automatically with the correct multipart boundary
client.interceptors.request.use((config) => {
    if (config.data instanceof FormData) {
        delete config.headers['Content-Type']
    }
    return config
})

// Response flags
let isRefreshing = false
let refreshQueue: Array<(value: unknown) => void> = []

// Async queue of errors on resolve
const drainQueue = (error?: unknown) => {
    refreshQueue.forEach((resolve) => resolve(error))
    refreshQueue = []
}

client.interceptors.response.use(
    (response: AxiosResponse) => response,

    // Retry handler
    async (error) => {
        // Unpack response
        const original: RetryableRequest = error.config
        const is401 = error.response?.status === 401
        const isRefreshEndpoint = original.url?.includes('/auth/token/refresh/')
        const isAuthEndpoint =
            original?.url?.includes('/auth/login/') ||
            original?.url?.includes('/auth/register/') ||
            original?.url?.includes('/auth/registration/')
        const alreadyRetried = original._retry

        // If it wasnt a 401, is a refresh endpoint and we've already tried, reject.
        if (!is401 || isRefreshEndpoint || alreadyRetried || isAuthEndpoint) {
            return Promise.reject(normaliseError(error))
        }

        // If Add the reponse resolve fn to the refresh queue to resolve later.
        if (isRefreshing) {
            return new Promise((resolve) => {
                refreshQueue.push(resolve)
            }).then(() => client(original))
        }

        // Set response flags
        original._retry = true
        isRefreshing = true

        // Refresh logic
        try {
            // Get a new token using existing refresh token
            await client.post('/auth/token/refresh/')

            // Resolve the responses in the queue if successful
            drainQueue()

            // Return the original response
            return client(original)
        } catch (refreshError) {
            // No refresh token, add the refresh error to the queue
            drainQueue(refreshError)

            // Reject
            return Promise.reject(normaliseError(refreshError))
        } finally {
            // Important, set isRefreshing false to prevent infinte loops.
            isRefreshing = false
        }
    },
)

// API Helpers
export const api = {
    get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> =>
        client.get<T>(url, config).then((r) => r.data),

    post: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> =>
        client.post<T>(url, data, config).then((r) => r.data),

    patch: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> =>
        client.patch<T>(url, data, config).then((r) => r.data),

    put: <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> =>
        client.put<T>(url, data, config).then((r) => r.data),

    delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> =>
        client.delete<T>(url, config).then((r) => r.data),
}

export { client }
