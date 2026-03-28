import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * @fileoverview Utility for conditionally joining CSS class names and
 * resolving Tailwind CSS conflicts.
 */

/**
 * Merges class names and resolves conflicting Tailwind CSS classes.
 *
 * This function uses 'clsx' to handle conditional class logic and
 * 'tailwind-merge' to ensure that the last conflicting class (e.g.,
 * padding or margin) takes precedence in the final output string.
 *
 * Args:
 * inputs: A variadic list of class values, which can include strings,
 * arrays, or objects of booleans.
 *
 * Returns:
 * A single merged string of CSS classes.
 */
export function cn(...inputs: ClassValue[]): string {
    return twMerge(clsx(inputs))
}
