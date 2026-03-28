/**
 * @fileoverview Defines shared TypeScript interfaces for database models
 * and API response structures.
 */

/**
 * Base metadata common to all entities following the Apex standard.
 */
export interface ApexModel {
    id: string
    created_at: string
    updated_at: string
}

/**
 * Standardized lookup model for categorized or reference data.
 * Extends the base ApexModel with display labels and identification codes.
 */
export interface NormalisedLookupModel extends ApexModel {
    code: string
    label: string
    order_index?: number
    description?: string
}

/**
 * Lightweight interface for simple key-value selection lists.
 */
export interface LabelLookup {
    id: string
    label: string
}

/**
 * Standardized container for paginated list responses from the API.
 * * @template T The type of the records returned in the results array.
 */
export interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}
