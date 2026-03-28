import { create } from 'zustand'
import { db } from './schema'
import type { LocalSession, LocalExerciseRecord, LocalSetRecord } from './schema'

/** Generates a random UUID for local record identification. */
const uuid = () => crypto.randomUUID()

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
        // Find the most recent unsynced session for this workout.
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

        // Identify the last recorded exercise to resume session state accurately.
        const lastExercise = exercises.filter((e) => !e.skipped && !e.synced).at(-1) ?? null

        set({ activeSession: session, activeExercise: lastExercise })
        return session
    },

    clearSession: () => {
        set({ activeSession: null, activeExercise: null })
    },
}))
