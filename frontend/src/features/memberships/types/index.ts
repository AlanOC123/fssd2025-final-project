import type { ApexModel } from '@/shared/types/base'

export type MembershipStatusCode =
    | 'PENDING_TRAINER_REVIEW'
    | 'ACTIVE'
    | 'REJECTED'
    | 'DISSOLVED_BY_CLIENT'
    | "DISSOLVED_BY_TRAINER"

export interface Membership extends ApexModel {
    trainer_name: string
    client_name: string
    status_id: string
    status_code: MembershipStatusCode
    status_label: string
    requested_at: string
    responded_at: string | null
    started_at: string | null
    ended_at: string | null
}
