import type { ApexModel } from "@/shared/types/base";

export interface CreateWorkoutPayload {
    program_phase_id: string
    workout_name: string
    planned_date?: string | null
}

export interface CreateWorkoutExercisePayload {
    workout_id: string
    exercise_id: string
    order: number
    sets_prescribed: number
    trainer_notes?: string
}

export interface CreateWorkoutSetPayload {
    workout_exercise_id: string
    set_order: number
    reps_prescribed: number
    weight_prescribed: number
}

export interface ExerciseRef {
    id: string
    exercise_name: string
    instructions: string
    safety_tips: string
    experience_level: { id: string; label: string }
    equipment: { id: string; label: string }[]
}

export interface WorkoutListItem extends ApexModel {
    workout_name: string
    planned_date: string | null
    program_phase_id: string
    has_session: boolean
}

export interface WorkoutSet extends ApexModel {
    set_order: number
    reps_prescribed: number
    weight_prescribed: number
}

export interface WorkoutExercise extends ApexModel {
    exercise_id: string
    exercise_name: string
    order: number
    sets_prescribed: number
    trainer_notes: string
    exercise: {
        id: string
        exercise_name: string
        instructions: string
        safety_tips: string
        experience_level: { id: string; label: string }
        equipment: { id: string; label: string }[]
    }
    sets: WorkoutSet[]
}

export interface WorkoutDetail extends ApexModel {
    workout_name: string
    planned_date: string | null
    program_phase_id: string
    exercises: WorkoutExercise[]
    has_session: boolean
}
