import Dexie, { type EntityTable } from 'dexie'
import { z } from 'zod'

/**
 * Zod schema for a local workout session record.
 */
const localSessionSchema = z.object({
    /** Unique local identifier (UUID). */
    localId: z.uuid(),
    /** The server-side workout identifier. */
    workoutId: z.uuid(),
    /** Timestamp indicating when the session began. */
    started_at: z.iso.datetime(),
    /** Timestamp indicating when the session ended, if applicable. */
    finished_at: z.iso.datetime().nullable(),
    /** Flag indicating if the record has been uploaded to the server. */
    synced: z.boolean(),
    /** The server-side record identifier after synchronization. */
    serverId: z.uuid().nullable(),
})

/**
 * Zod schema for a local exercise record within a session.
 */
const localExerciseRecordSchema = z.object({
    /** Unique local identifier (UUID). */
    localId: z.uuid(),
    /** Identifier linking to the local session. */
    localSessionId: z.uuid(),
    /** The server-side workout exercise identifier. */
    workoutExerciseId: z.uuid(),
    /** Whether the exercise was skipped during the session. */
    skipped: z.boolean(),
    /** Timestamp indicating when the exercise was started. */
    started_at: z.iso.datetime(),
    /** Sync status flag. */
    synced: z.boolean(),
    /** The server-side record identifier after synchronization. */
    serverId: z.uuid().nullable(),
})

/**
 * Zod schema for a local set performance record.
 */
const localSetRecordSchema = z.object({
    /** Unique local identifier (UUID). */
    localId: z.uuid(),
    /** Identifier linking to the local exercise record. */
    localExerciseId: z.uuid(),
    /** The server-side workout set identifier. */
    workoutSetId: z.uuid(),
    /** Whether the set was skipped. */
    skipped: z.boolean(),
    /** Number of repetitions performed. */
    repsCompleted: z.number(),
    /** Weight load used for the set. */
    weightCompleted: z.number(),
    /** Optional subjective difficulty rating (RPE). */
    difficultyRating: z.number().nullable(),
    /** Optional repetitions in reserve (RIR). */
    repsInReserve: z.number().nullable(),
    /** Timestamp of set completion. */
    completedAt: z.iso.datetime(),
    /** Sync status flag. */
    synced: z.boolean(),
})

/** Represents a workout session stored in the local IndexedDB. */
export type LocalSession = z.infer<typeof localSessionSchema>

/** Represents an exercise record stored in the local IndexedDB. */
export type LocalExerciseRecord = z.infer<typeof localExerciseRecordSchema>

/** Represents a set performance record stored in the local IndexedDB. */
export type LocalSetRecord = z.infer<typeof localSetRecordSchema>

/**
 * Local IndexedDB database for offline-first workout tracking.
 *
 * This class handles the storage and retrieval of session, exercise, and set
 * records, allowing for offline data persistence before synchronization.
 */
export class ApexDB extends Dexie {
    /** Table for storing workout session metadata. */
    sessions!: EntityTable<LocalSession, 'localId'>
    /** Table for storing exercise-level records. */
    exerciseRecords!: EntityTable<LocalExerciseRecord, 'localId'>
    /** Table for storing individual set performance data. */
    setRecords!: EntityTable<LocalSetRecord, 'localId'>

    /**
     * Initializes the ApexDB with the specified stores and versions.
     */
    constructor() {
        super('ApexDb')

        this.version(1).stores({
            sessions: '&localId, workoutId, synced',
            exerciseRecords: '&localId, localSessionId, workoutExerciseId, synced',
            setRecords: '&localId, localExerciseId, workoutSetId, synced',
        })
    }
}

/**
 * Global instance of the ApexDB local database.
 */
export const db = new ApexDB()
