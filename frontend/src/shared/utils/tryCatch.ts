/**
 * @fileoverview Provides types and utilities for the Result pattern, enabling
 * explicit error handling without mandatory try-catch blocks.
 */

/**
 * Represents a successful operation outcome.
 *
 * @template T The type of the data returned on success.
 */
export type Success<T> = {
    /** The successful result data. */
    data: T
    /** Always null in a success state. */
    error: null
}

/**
 * Represents a failed operation outcome.
 *
 * @template E The type of the error object.
 */
export type Failure<E> = {
    /** Always null in a failure state. */
    data: null
    /** The error object encountered during the operation. */
    error: E
}

/**
 * A discriminated union representing either a success or a failure.
 *
 * @template T The type of the successful data.
 * @template E The type of the error (defaults to Error).
 */
export type Result<T, E = Error> = Success<T> | Failure<E>

/**
 * Executes a promise and returns a standardized Result object.
 *
 * This helper promotes "errors as values" by catching exceptions internally
 * and returning them as part of a structured object.
 *
 * @template T The expected type of the resolved promise value.
 * @template E The expected type of the caught error.
 * Args:
 * promise: The asynchronous operation to execute.
 * Returns:
 * A promise resolving to a Result object containing either the data
 * or the caught error.
 */
export async function tryCatch<T, E = Error>(promise: Promise<T>): Promise<Result<T, E>> {
    try {
        const data = await promise
        return { data, error: null }
    } catch (error) {
        return { data: null, error: error as E }
    }
}
