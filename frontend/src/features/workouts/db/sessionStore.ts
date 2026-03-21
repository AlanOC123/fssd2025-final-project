import { create } from 'zustand'
import { db } from './schema'
import type { LocalSession, LocalExerciseRecord, LocalSetRecord } from './schema'

const uuid = () => crypto.randomUUID()

interface SessionState {
    activeSession: LocalSession | null
    activeExercise: LocalExerciseRecord | null

    startSession: (workoutId: string) => Promise<LocalSession>
    startExercise: (workoutExerciseId: string) => Promise<LocalExerciseRecord>
    skipExercise: (workoutExerciseId: string) => Promise<LocalExerciseRecord>

    logSet: (
        params: Pick<LocalSetRecord, 'workoutSetId' | 'repsCompleted' | 'weightCompleted'> & {
            difficultyRating?: number | null
            repsInReserve?: number | null
        },
    ) => Promise<LocalSetRecord>

    skipSet: (workoutSetId: string) => Promise<LocalSetRecord>
    finishSession: () => Promise<LocalSession>
    loadSession: (workoutId: string) => Promise<LocalSession | null>
    clearSession: () => void
}

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
            finished_at: new Date().toISOString()
        }

        await db.sessions.update(activeSession.localId, { finished_at: finished.finished_at })

        set({ activeSession: finished })
        return finished
    },

    loadSession: async (workoutId: string) => {
        const session = await db.sessions
            .where('workoutId').equals(workoutId)
            .filter((s) => !s.synced)
            .first()

        if (!session) return null

        const exercises = await db.exerciseRecords
            .where('localSessionId').equals(session.localId)
            .toArray()

        const lastExercise = exercises
        .filter((e) => !e.skipped && !e.synced)
        .at(-1) ?? null

        set({ activeSession: session, activeExercise: lastExercise })
        return session
    },

    clearSession: () => {
        set({ activeSession: null, activeExercise: null })
    },
}))
