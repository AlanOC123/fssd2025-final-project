import type { ApexModel, LabelLookup } from "@/shared/types/base";

export interface TrainerMatchProfile extends ApexModel {
    first_name: string
    last_name: string
    email: string
    company: string
    website: string
    logo: string
    accepted_goals: LabelLookup[]
    accepted_levels: LabelLookup[]
}
