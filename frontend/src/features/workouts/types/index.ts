import type { ApexModel } from "@/shared/types/base";

export interface WorkoutListItem extends ApexModel {
    workout_name: string
    planned_date: string | null
    program_phase_id: string
}

export interface WorkoutExercise extends ApexModel {
    exercise_id: string
    exercise_name: string
    order: number
    sets_prescribed: number
    trainer_notes: string
}

export interface WorkoutDetail extends ApexModel {
    workout_name: string
    planned_date: string | null
    program_phase_id: string
    exercises: WorkoutExercise[]
}
