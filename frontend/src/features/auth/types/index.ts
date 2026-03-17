import type { ApexModel, LabelLookup } from '@/shared/types/base'

export interface ClientProfile extends ApexModel {
    goal?: LabelLookup
    level?: LabelLookup
    avatar: string
}

export interface TrainerProfile extends ApexModel {
    accepted_goals: LabelLookup[]
    accepted_levels: LabelLookup[]
    company: string
    website?: string
    logo: string
}

export type UserRole = 'trainer' | 'client' | 'admin' | null

export interface AuthUser extends ApexModel {
    email: string
    first_name: string
    last_name: string
    full_name: string
    is_trainer: boolean
    is_client: boolean
    profile: ClientProfile | TrainerProfile | null,
    role: UserRole
}

export interface LoginCredentials {
    email: string
    password: string
}

export interface LoginResponse {
    access: string
    access_expiration: string
    refresh: string
    refresh_expiration: string
    user: AuthUser
}

export interface AuthState {
    user: AuthUser | null
    isAuthenticated: boolean
    isLoading: boolean
}
