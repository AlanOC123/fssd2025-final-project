export interface LoadHistoryEntry {
    session_id: string
    workout_name: string
    completed_at: string
    one_rep_max: string
    session_load: string
    target_load: string | null
    weight_floor: string | null
    weight_ceiling: string | null
    muscle_breakdown: {
        muscle_id: string
        muscle_label: string
        muscle_group: string | null
        role: string
        load: string
    }[]
}

export type TimeRange = 'week' | 'month' | 'phase' | '3month' | 'year'

export interface ChartPoint {
    date: string
    rawDate: Date
    oneRepMax: number
    sessionLoad: number
    targetLoad: number | null
    weightFloor: number | null
    weightCeiling: number | null
}
