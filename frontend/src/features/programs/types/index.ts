import type { ApexModel, LabelLookup } from '@/shared/types/base'

export type ProgramStatusCode =
    | 'CREATING'
    | 'OUT_FOR_REVIEW'
    | 'READY_TO_BEGIN'
    | 'IN_PROGRESS'
    | 'COMPLETED'
    | 'ABANDONED'

export type PhaseStatusCode = 'PLANNED' | 'NEXT' | 'ACTIVE' | 'COMPLETED' | 'SKIPPED' | 'ARCHIVED'

export interface ProgramPhase extends ApexModel {
    program_id: string
    phase_option: LabelLookup & { default_duration_days: number; default_duration_weeks: number }
    phase_name: string
    phase_goal: string
    sequence_order: number
    status: LabelLookup & { code: PhaseStatusCode }
    trainer_notes: string
    client_notes: string
    planned_start_date: string
    planned_end_date: string
    actual_start_date: string | null
    actual_end_date: string | null
    started_at: string | null
    completed_at: string | null
    skipped_at: string | null
    skipped_reason: string
    archived_at: string | null
    archived_reason: string
    duration_days: number
    duration_weeks: number
}

export interface ProgramListItem extends ApexModel {
    program_name: string
    version: number
    trainer_client_membership_id: string
    status: LabelLookup & { code: ProgramStatusCode }
    training_goal: LabelLookup
    experience_level: LabelLookup
    planned_start_date: string | null
    planned_end_date: string | null
    actual_start_date: string | null
    actual_end_date: string | null
    program_duration_days: number
    program_duration_weeks: number
    has_created_phases: boolean
    number_of_completed_phases: number
    number_of_skipped_phases: number
    number_of_archived_phases: number
    all_phases_finished: boolean
    remaining_phases: ProgramPhase[]
    submitted_for_review_at: string | null
    reviewed_at: string | null
    started_at: string | null
    completed_at: string | null
    abandoned_at: string | null
}

export interface ProgramDetail extends ApexModel {
    program_name: string
    version: number
    trainer_client_membership_id: string
    status: LabelLookup & { code: ProgramStatusCode }
    training_goal: LabelLookup
    experience_level: LabelLookup
    created_by_trainer_id: string | null
    last_edited_by_id: string | null
    planned_start_date: string | null
    planned_end_date: string | null
    actual_start_date: string | null
    actual_end_date: string | null
    program_duration_days: number
    program_duration_weeks: number
    has_created_phases: boolean
    number_of_completed_phases: number
    number_of_skipped_phases: number
    number_of_archived_phases: number
    all_phases_finished: boolean
    phases: ProgramPhase[]
    submitted_for_review_at: string | null
    reviewed_at: string | null
    started_at: string | null
    completed_at: string | null
    abandoned_at: string | null
    review_notes: string
    completion_notes: string
    abandonment_reason: string
}
