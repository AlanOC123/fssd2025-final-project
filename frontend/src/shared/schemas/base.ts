import { z } from 'zod'

export const apexModelSchema = z.object({
    id: z.uuid(),
    created_at: z.iso.datetime(),
    updated_at: z.iso.datetime(),
})

export const normalisedLookupModelSchema = apexModelSchema.extend({
    code: z.string(),
    label: z.string(),
    order_index: z.number().optional(),
    description: z.string().optional(),
})

export const labelLookupSchema = z.object({
    id: z.uuid(),
    label: z.string(),
})

export const paginatedResponseSchema = <T extends z.ZodAny>(itemSchema: T) =>
    z.object({
        count: z.number(),
        next: z.string().optional(),
        previous: z.string().optional(),
        results: z.array(itemSchema),
    })

export type ApexModelSchema = z.infer<typeof apexModelSchema>
export type NormalisedModelSchema = z.infer<typeof normalisedLookupModelSchema>
export type LabelLookupSchema = z.infer<typeof labelLookupSchema>
