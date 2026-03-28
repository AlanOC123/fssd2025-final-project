import axios, {
    type AxiosInstance,
    type AxiosRequestConfig,
    type AxiosResponse,
    type InternalAxiosRequestConfig,
} from 'axios'

import { normaliseError, type ApiError } from '@/shared/utils/errors'

export type { ApiError }

/**
 * Extension of InternalAxiosRequestConfig to track retry attempts.
 */
interface RetryableRequest extends InternalAxiosRequestConfig {
    /** Indicates if the request has already been retried following a 401. */
    _retry?: boolean
}

/**
 * Base Axios instance configured for the application API.
 */
const client: AxiosInstance = axios.create({
    baseURL: '/api/v1',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
    },
})

/**
 * Request interceptor to handle multipart/form-data.
 * * Removes the manual Content-Type header when sending FormData to allow
 * the browser/Axios to automatically set the boundary string.
 */
client.interceptors.request.use((config) => {
    if (config.data instanceof FormData) {
        delete config.headers['Content-Type']
    }
    return config
})

let isRefreshing = false
let refreshQueue: Array<(value: unknown) => void> = []

/**
 * Resolves or rejects all pending promises in the refresh queue.
 *
 * Args:
 * error: Optional error to pass to the resolvers if the refresh failed.
 */
const drainQueue = (error?: unknown) => {
    refreshQueue.forEach((resolve) => resolve(error))
    refreshQueue = []
}

/**
 * Response interceptor for handling global error states and token refreshing.
 *
 * Implements a thread-safe-like queue for 401 Unauthorized responses. When a
 * session expires, it attempts to refresh the token and retries all
 * failed requests once the new token is obtained.
 *
 * Returns:
 * The successful response or a retried request promise.
 *
 * Throws:
 * ApiError: Normalised error object if the request fails or refresh is invalid.
 */
client.interceptors.response.use(
    (response: AxiosResponse) => response,

    async (error) => {
        const original: RetryableRequest = error.config
        const is401 = error.response?.status === 401
        const isRefreshEndpoint = original.url?.includes('/auth/token/refresh/')
        const isAuthEndpoint =
            original?.url?.includes('/auth/login/') ||
            original?.url?.includes('/auth/register/') ||
            original?.url?.includes('/auth/registration/')
        const alreadyRetried = original._retry

        // Guard clause to prevent retry loops on auth endpoints or repeated failures.
        if (!is401 || isRefreshEndpoint || alreadyRetried || isAuthEndpoint) {
            return Promise.reject(normaliseError(error))
        }

        // If a refresh is already in progress, queue this request.
        if (isRefreshing) {
            return new Promise((resolve) => {
                refreshQueue.push(resolve)
            }).then(() => client(original))
        }

        original._retry = true
        isRefreshing = true

        try {
            await client.post('/auth/token/refresh/')
            drainQueue()
            return client(original)
        } catch (refreshError) {
            drainQueue(refreshError)
            return Promise.reject(normaliseError(refreshError))
        } finally {
            isRefreshing = false
        }
    },
)

/**
 * Higher-level API utility for type-safe HTTP requests.
 */
export const api = {
    /**
     * Args:
     * url: Request destination.
     * config: Optional Axios configuration.
     * Returns:
     * The parsed data of type T.
     */
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
