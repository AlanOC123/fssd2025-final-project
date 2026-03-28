import { useState, useEffect } from 'react'

/**
 * Custom hook that debounces a value change by a specified delay.
 * * Useful for limiting the frequency of expensive operations, such as
 * API calls or filtering logic triggered by rapid user input.
 *
 * Args:
 * value: The input value to be debounced.
 * delay: The time in milliseconds to wait before updating the debounced value.
 * * Returns:
 * The most recent value after the specified delay has passed.
 */
export function useDebounce<T>(value: T, delay: number): T {
    const [debouncedValue, setDebouncedValue] = useState<T>(value)

    useEffect(() => {
        /**
         * Update the state only after the specified delay.
         */
        const timer = setTimeout(() => setDebouncedValue(value), delay)

        /**
         * Clean up the timeout if the value or delay changes before the
         * timer completes, effectively resetting the debounce period.
         */
        return () => clearTimeout(timer)
    }, [value, delay])

    return debouncedValue
}
