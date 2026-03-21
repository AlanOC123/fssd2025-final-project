import Dexie, { type EntityTable } from 'dexie'
import { z } from 'zod'

const localSessionSchema = z.object({
    localId: z.uuid(),
    workoutId: z.uuid(),
    started_at: z.iso.datetime(),
    finished_at: z.iso.datetime().nullable(),
    synced: z.boolean(),
    serverId: z.uuid().nullable(),
})

const localExerciseRecordSchema = z.object({
    localId: z.uuid(),
    localSessionId: z.uuid(),
    workoutExerciseId: z.uuid(),
    skipped: z.boolean(),
    started_at: z.iso.datetime(),
    synced: z.boolean(),
    serverId: z.uuid().nullable(),
})

const localSetRecordSchema = z.object({
    localId: z.uuid(),
    localExerciseId: z.uuid(),
    workoutSetId: z.uuid(),
    skipped: z.boolean(),
    repsCompleted: z.number(),
    weightCompleted: z.number(),
    difficultyRating: z.number().nullable(),
    repsInReserve: z.number().nullable(),
    completedAt: z.iso.datetime(),
    synced: z.boolean(),
})

export type LocalSession = z.infer<typeof localSessionSchema>
export type LocalExerciseRecord = z.infer<typeof localExerciseRecordSchema>
export type LocalSetRecord = z.infer<typeof localSetRecordSchema>

export class ApexDB extends Dexie {
    sessions!: EntityTable<LocalSession, 'localId'>
    exerciseRecords!: EntityTable<LocalExerciseRecord, 'localId'>
    setRecords!: EntityTable<LocalSetRecord, 'localId'>

    constructor() {
        super('ApexDb')

        this.version(1).stores({
            sessions: '&localId, workoutId, synced',
            exerciseRecords: '&localId, localSessionId, workoutExerciseId, synced',
            setRecords: '&localId, localExerciseId, workoutSetId, synced',
        })
    }
}

export const db = new ApexDB()
