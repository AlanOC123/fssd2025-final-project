import { z } from 'zod'

/**
 * Base schema for all models following the Apex standard.
 * * Defines the core metadata fields present in almost every database entity.
 */
export const apexModelSchema = z.object({
    id: z.uuid(),
    created_at: z.string().datetime(),
    updated_at: z.string().datetime(),
})

/**
 * Schema for standard lookup or reference data.
 * * Extends the base model with fields for display labels, unique codes,
 * and optional ordering/descriptions.
 */
export const normalisedLookupModelSchema = apexModelSchema.extend({
    code: z.string(),
    label: z.string(),
    order_index: z.number().optional(),
    description: z.string().optional(),
})

/**
 * Lightweight schema for dropdowns or simple selection lists.
 */
export const labelLookupSchema = z.object({
    id: z.uuid(),
    label: z.string(),
})

/**
 * Helper function to generate a standard paginated response structure.
 *
 * Args:
 * itemSchema: The Zod schema for the individual items in the results array.
 * * Returns:
 * A Zod object schema for the paginated response.
 */
export const paginatedResponseSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
    z.object({
        count: z.number(),
        next: z.string().nullable().optional(),
        previous: z.string().nullable().optional(),
        results: z.array(itemSchema),
    })

export type ApexModelSchema = z.infer<typeof apexModelSchema>
export type NormalisedModelSchema = z.infer<typeof normalisedLookupModelSchema>
export type LabelLookupSchema = z.infer<typeof labelLookupSchema>
