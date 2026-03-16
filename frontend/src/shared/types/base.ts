export interface ApexModel {
    id: string
    created_at: string
    updated_at: string
}

export interface NormalisedLookupModel extends ApexModel {
    code: string
    label: string
    order_index?: number
    description?: string
}

export interface LabelLookup {
    id: string
    label: string
}

// Pagnination
export interface PaginatedResponse<T> {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}
