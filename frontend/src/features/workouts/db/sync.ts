import { create } from 'zustand'
import { api } from '@/shared/api/client'
import { tryCatch } from '@/shared/utils/tryCatch'
import { db } from './schema'
import type { LocalSession, LocalExerciseRecord, LocalSetRecord } from './schema'

/** Generates a random UUID for local record identification. */
const uuid = () => crypto.randomUUID()

// ─── API Response Interfaces ─────────────────────────────────────────────────

/** Represents the server response for session operations. */
interface SessionResponse {
    id: string
}

/** Represents the server response for exercise record operations. */
interface ExerciseRecordResponse {
    id: string
}

/** Represents the server response for set record operations. */
interface SetRecordResponse {
    id: string
}

// ─── API Call Helpers ────────────────────────────────────────────────────────

/**
 * Sends a request to start a workout session on the server.
 *
 * @param workoutId Unique identifier of the workout.
 * @return A promise resolving to the session response.
 */
const startSessionApi = (workoutId: string): Promise<SessionResponse> =>
    api.post<SessionResponse>('/workouts/workout-sessions/start/', { workout_id: workoutId })

/**
 * Sends a request to finalize a workout session on the server.
 *
 * @param serverId The server-side identifier of the session.
 * @return A promise resolving to the session response.
 */
const finishSessionApi = (serverId: string): Promise<SessionResponse> =>
    api.post<SessionResponse>(`/workouts/workout-sessions/${serverId}/finish/`)

/**
 * Registers the start of an exercise on the server.
 *
 * @param workoutExerciseId The ID of the workout exercise definition.
 * @param sessionServerId The ID of the parent session on the server.
 * @return A promise resolving to the exercise record response.
 */
const startExerciseApi = (
    workoutExerciseId: string,
    sessionServerId: string,
): Promise<ExerciseRecordResponse> =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/start/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

/**
 * Registers an exercise as skipped on the server.
 *
 * @param workoutExerciseId The ID of the workout exercise definition.
 * @param sessionServerId The ID of the parent session on the server.
 * @return A promise resolving to the exercise record response.
 */
const skipExerciseApi = (
    workoutExerciseId: string,
    sessionServerId: string,
): Promise<ExerciseRecordResponse> =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/skip/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

/**
 * Uploads a completed set record to the server.
 *
 * @param set The local set record data.
 * @param exerciseServerId The ID of the parent exercise record on the server.
 * @return A promise resolving to the set record response.
 */
const completeSetApi = (
    set: LocalSetRecord,
    exerciseServerId: string,
): Promise<SetRecordResponse> =>
    api.post<SetRecordResponse>('/workouts/set-records/complete/', {
        workout_set_id: set.workoutSetId,
        exercise_record_id: exerciseServerId,
        reps_completed: set.repsCompleted,
        weight_completed: set.weightCompleted,
        ...(set.difficultyRating != null && { difficulty_rating: set.difficultyRating }),
        ...(set.repsInReserve != null && { reps_in_reserve: set.repsInReserve }),
    })

/**
 * Registers a set as skipped on the server.
 *
 * @param workoutSetId The ID of the workout set definition.
 * @param exerciseServerId The ID of the parent exercise record on the server.
 * @return A promise resolving to the set record response.
 */
const skipSetApi = (workoutSetId: string, exerciseServerId: string): Promise<SetRecordResponse> =>
    api.post<SetRecordResponse>('/workouts/set-records/skip/', {
        workout_set_id: workoutSetId,
        exercise_record_id: exerciseServerId,
    })

// ─── Sync Error Handling ─────────────────────────────────────────────────────

/**
 * Custom error class for synchronization failures.
 */
export class SyncError extends Error {
    /**
     * Initializes a new SyncError.
     *
     * @param message Human-readable error message.
     * @param step The specific synchronization phase that failed.
     * @param cause The underlying error or API failure.
     */
    constructor(
        message: string,
        public readonly step: 'session' | 'exercise' | 'set' | 'finish',
        public readonly cause?: unknown,
    ) {
        super(message)
        this.name = 'SyncError'
    }
}

// ─── Synchronization Logic ───────────────────────────────────────────────────

/**
 * Synchronizes a local workout session and its child records with the server.
 *
 * This function handles the sequential upload of the session, exercise records,
 * and set records, updating the local database with server IDs and sync status.
 *
 * @param localSession The local session record to synchronize.
 * @throws SyncError If any step of the synchronization process fails.
 * @return A promise that resolves when the session is fully synchronized.
 */
export async function syncSession(localSession: LocalSession): Promise<void> {
    let sessionServerId: string

    // 1. Sync Session
    if (localSession.serverId) {
        sessionServerId = localSession.serverId
    } else {
        const { data, error } = await tryCatch(startSessionApi(localSession.workoutId))
        if (error) throw new SyncError('Failed to start session on server', 'session', error)
        sessionServerId = data.id
        await db.sessions.update(localSession.localId, { serverId: sessionServerId })
    }

    // 2. Sync Exercises
    const exerciseRecords: LocalExerciseRecord[] = await db.exerciseRecords
        .where('localSessionId')
        .equals(localSession.localId)
        .sortBy('started_at')

    for (const exercise of exerciseRecords) {
        let exerciseServerId: string

        if (exercise.serverId) {
            exerciseServerId = exercise.serverId
        } else {
            const exerciseRes = exercise.skipped
                ? await tryCatch(skipExerciseApi(exercise.workoutExerciseId, sessionServerId))
                : await tryCatch(startExerciseApi(exercise.workoutExerciseId, sessionServerId))

            const { data, error } = exerciseRes
            if (error) {
                throw new SyncError(
                    `Failed to sync exercise ${exercise.workoutExerciseId}`,
                    'exercise',
                    error,
                )
            }

            exerciseServerId = data.id
            await db.exerciseRecords.update(exercise.localId, {
                serverId: exerciseServerId,
                synced: true,
            })
        }

        if (exercise.skipped) continue

        // 3. Sync Sets
        const setRecords: LocalSetRecord[] = await db.setRecords
            .where('localExerciseId')
            .equals(exercise.localId)
            .sortBy('completedAt')

        for (const set of setRecords) {
            if (set.synced) continue

            const setRes = set.skipped
                ? await tryCatch(skipSetApi(set.workoutSetId, exerciseServerId))
                : await tryCatch(completeSetApi(set, exerciseServerId))

            const { error } = setRes
            if (error) throw new SyncError(`Failed to sync set ${set.workoutSetId}`, 'set', error)

            await db.setRecords.update(set.localId, { synced: true })
        }
    }

    // 4. Finish session
    if (!localSession.synced) {
        const { error } = await tryCatch(finishSessionApi(sessionServerId))
        if (error) throw new SyncError('Failed to finish session on server', 'finish', error)
        await db.sessions.update(localSession.localId, { synced: true })
    }
}

// ─── Store Implementation ────────────────────────────────────────────────────

/**
 * Interface representing the state and actions for managing a workout session.
 */
interface SessionState {
    /** The currently active session record, or null if no session is in progress. */
    activeSession: LocalSession | null
    /** The currently active exercise record within the session. */
    activeExercise: LocalExerciseRecord | null

    /**
     * Initializes a new workout session and persists it to the local database.
     *
     * @param workoutId The unique identifier of the workout being started.
     * @return A promise resolving to the newly created LocalSession.
     */
    startSession: (workoutId: string) => Promise<LocalSession>

    /**
     * Starts a specific exercise within the active session.
     *
     * @param workoutExerciseId The ID of the exercise to start.
     * @throws Error if there is no active session in the store.
     * @return A promise resolving to the created exercise record.
     */
    startExercise: (workoutExerciseId: string) => Promise<LocalExerciseRecord>

    /**
     * Records an exercise as skipped within the active session.
     *
     * @param workoutExerciseId The ID of the exercise being skipped.
     * @throws Error if there is no active session in the store.
     * @return A promise resolving to the skipped exercise record.
     */
    skipExercise: (workoutExerciseId: string) => Promise<LocalExerciseRecord>

    /**
     * Logs a completed set for the active exercise.
     *
     * @param params Object containing set performance data.
     * @throws Error if there is no active exercise in the store.
     * @return A promise resolving to the created set record.
     */
    logSet: (
        params: Pick<LocalSetRecord, 'workoutSetId' | 'repsCompleted' | 'weightCompleted'> & {
            difficultyRating?: number | null
            repsInReserve?: number | null
        },
    ) => Promise<LocalSetRecord>

    /**
     * Records a set as skipped for the active exercise.
     *
     * @param workoutSetId The ID of the set being skipped.
     * @throws Error if there is no active exercise in the store.
     * @return A promise resolving to the skipped set record.
     */
    skipSet: (workoutSetId: string) => Promise<LocalSetRecord>

    /**
     * Finalizes the current session by adding a completion timestamp.
     *
     * @throws Error if there is no active session in the store.
     * @return A promise resolving to the updated session record.
     */
    finishSession: () => Promise<LocalSession>

    /**
     * Attempts to load an existing, unsynced session from the local database.
     *
     * @param workoutId The ID of the workout to look for.
     * @return A promise resolving to the found session or null if none exists.
     */
    loadSession: (workoutId: string) => Promise<LocalSession | null>

    /**
     * Clears the active session and exercise from the store state.
     */
    clearSession: () => void
}

/**
 * Hook for accessing the workout session store.
 *
 * Manages the lifecycle of a workout including session initialization,
 * exercise tracking, and set performance logging with IndexedDB persistence.
 */
export const useSessionStore = create<SessionState>((set, get) => ({
    activeSession: null,
    activeExercise: null,

    startSession: async (workoutId) => {
        const now = new Date().toISOString()
        const session: LocalSession = {
            localId: uuid(),
            workoutId,
            started_at: now,
            finished_at: null,
            synced: false,
            serverId: null,
        }
        await db.sessions.add(session)
        set({ activeSession: session, activeExercise: null })
        return session
    },

    startExercise: async (workoutExerciseId: string) => {
        const { activeSession } = get()

        if (!activeSession) throw new Error('No active session')

        const now = new Date().toISOString()
        const record: LocalExerciseRecord = {
            localId: uuid(),
            localSessionId: activeSession.localId,
            workoutExerciseId,
            skipped: false,
            started_at: now,
            serverId: null,
            synced: false,
        }

        await db.exerciseRecords.add(record)
        set({ activeExercise: record })
        return record
    },

    skipExercise: async (workoutExerciseId: string) => {
        const { activeSession } = get()

        if (!activeSession) throw new Error('No active session')

        const now = new Date().toISOString()
        const record: LocalExerciseRecord = {
            localId: uuid(),
            localSessionId: activeSession.localId,
            workoutExerciseId,
            skipped: true,
            started_at: now,
            serverId: null,
            synced: false,
        }

        await db.exerciseRecords.add(record)
        set({ activeExercise: record })
        return record
    },

    logSet: async ({
        workoutSetId,
        repsCompleted,
        weightCompleted,
        difficultyRating = null,
        repsInReserve = null,
    }) => {
        const { activeExercise } = get()
        if (!activeExercise) throw new Error('No active exercise')

        const record: LocalSetRecord = {
            localId: uuid(),
            localExerciseId: activeExercise.localId,
            workoutSetId,
            skipped: false,
            repsCompleted,
            weightCompleted,
            difficultyRating: difficultyRating ?? null,
            repsInReserve: repsInReserve ?? null,
            completedAt: new Date().toISOString(),
            synced: false,
        }

        await db.setRecords.add(record)
        return record
    },

    skipSet: async (workoutSetId: string) => {
        const { activeExercise } = get()
        if (!activeExercise) throw new Error('No active exercise')

        const record: LocalSetRecord = {
            localId: uuid(),
            localExerciseId: activeExercise.localId,
            workoutSetId,
            skipped: true,
            repsCompleted: 0,
            weightCompleted: 0,
            difficultyRating: null,
            repsInReserve: null,
            completedAt: new Date().toISOString(),
            synced: false,
        }

        await db.setRecords.add(record)
        return record
    },

    finishSession: async () => {
        const { activeSession } = get()
        if (!activeSession) throw new Error('No active session')

        const finished = {
            ...activeSession,
            finished_at: new Date().toISOString(),
        }

        await db.sessions.update(activeSession.localId, { finished_at: finished.finished_at })

        set({ activeSession: finished })
        return finished
    },

    loadSession: async (workoutId: string) => {
        const session = await db.sessions
            .where('workoutId')
            .equals(workoutId)
            .filter((s) => !s.synced)
            .first()

        if (!session) return null

        const exercises = await db.exerciseRecords
            .where('localSessionId')
            .equals(session.localId)
            .toArray()

        const lastExercise = exercises.filter((e) => !e.skipped && !e.synced).at(-1) ?? null

        set({ activeSession: session, activeExercise: lastExercise })
        return session
    },

    clearSession: () => {
        set({ activeSession: null, activeExercise: null })
    },
}))
