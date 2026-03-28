import axios from 'axios'

/**
 * @fileoverview Utility functions and interfaces for standardizing and
 * validating API error responses across the application.
 */

/**
 * Represents a standardized error object used throughout the application.
 */
export interface ApiError {
    /** HTTP status code or 0 if the request failed before a response. */
    status: number
    /** User-facing or internal error message. */
    message: string
    /** Optional detailed error information, often from the backend. */
    detail?: string | Record<string, string[]>
}

/**
 * Transforms an unknown error into a standardized ApiError object.
 *
 * Handles Axios-specific error structures to extract status codes and
 * backend details, while providing a fallback for generic errors.
 *
 * Args:
 * error: The raw error caught in a catch block or response interceptor.
 *
 * Returns:
 * A normalized ApiError object.
 */
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

/**
 * Type guard to determine if an unknown error matches the ApiError structure.
 *
 * Args:
 * error: The value to inspect.
 *
 * Returns:
 * True if the error is an object containing 'status' and 'message'.
 */
export function isApiError(error: unknown): error is ApiError {
    return typeof error === 'object' && error !== null && 'status' in error && 'message' in error
}
