import { api } from '@/shared/api/client'
import { db } from './schema'
import type { LocalSession, LocalExerciseRecord, LocalSetRecord } from './schema'

// ─── API response types ───────────────────────────────────────────────────────

interface SessionResponse {
    id: string
}
interface ExerciseRecordResponse {
    id: string
}
interface SetRecordResponse {
    id: string
}

// ─── API calls ────────────────────────────────────────────────────────────────

const startSession = (workoutId: string) =>
    api.post<SessionResponse>('/workouts/workout-sessions/start/', {
        workout_id: workoutId,
    })

const finishSession = (serverId: string) =>
    api.post<SessionResponse>(`/workouts/workout-sessions/${serverId}/finish/`)

const startExercise = (workoutExerciseId: string, sessionServerId: string) =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/start/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

const skipExercise = (workoutExerciseId: string, sessionServerId: string) =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/skip/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

const completeSet = (set: LocalSetRecord, exerciseServerId: string) =>
    api.post<SetRecordResponse>('/workouts/set-records/complete/', {
        workout_set_id: set.workoutSetId,
        exercise_record_id: exerciseServerId,
        reps_completed: set.repsCompleted,
        weight_completed: set.weightCompleted,
        ...(set.difficultyRating != null && { difficulty_rating: set.difficultyRating }),
        ...(set.repsInReserve != null && { reps_in_reserve: set.repsInReserve }),
    })

const skipSet = (workoutSetId: string, exerciseServerId: string) =>
    api.post<SetRecordResponse>('/workouts/set-records/skip/', {
        workout_set_id: workoutSetId,
        exercise_record_id: exerciseServerId,
    })

// ─── Sync ─────────────────────────────────────────────────────────────────────

export class SyncError extends Error {
    constructor(
        message: string,
        step: 'session' | 'exercise' | 'set' | 'finish',
        cause?: unknown,
    ) {
        super(message)
        this.name = 'SyncError'
    }
}

export async function syncSession(localSession: LocalSession): Promise<void> {
    // 1. Start session on the server
    let sessionServerId: string
    try {
        const res = await startSession(localSession.workoutId)
        sessionServerId = res.id
        await db.sessions.update(localSession.localId, {
            serverId: sessionServerId,
        })
    } catch (cause) {
        throw new SyncError('Failed to start session on server', 'session', cause)
    }

    // 2. Sync each exercise record in order
    const exerciseRecords: LocalExerciseRecord[] = await db.exerciseRecords
        .where('localSessionId')
        .equals(localSession.localId)
        .sortBy('started_at')

    for (const exercise of exerciseRecords) {
        let exerciseServerId: string

        try {
            const res = exercise.skipped
                ? await skipExercise(exercise.workoutExerciseId, sessionServerId)
                : await startExercise(exercise.workoutExerciseId, sessionServerId)

            exerciseServerId = res.id
            await db.exerciseRecords.update(exercise.localId, {
                serverId: exerciseServerId,
                synced: true,
            })
        } catch (cause) {
            throw new SyncError(
                `Failed to sync exercise ${exercise.workoutExerciseId}`,
                'exercise',
                cause,
            )
        }

        // Skip syncing sets for skipped exercises
        if (exercise.skipped) continue

        // 3. Sync each set record for this exercise in order
        const setRecords: LocalSetRecord[] = await db.setRecords
            .where('localExerciseId')
            .equals(exercise.localId)
            .sortBy('completedAt')

        for (const set of setRecords) {
            try {
                const res = set.skipped
                    ? await skipSet(set.workoutSetId, exerciseServerId)
                    : await completeSet(set, exerciseServerId)

                await db.setRecords.update(set.localId, {
                    synced: true,
                })
            } catch (cause) {
                throw new SyncError(`Failed to sync set ${set.workoutSetId}`, 'set', cause)
            }
        }
    }

    // 4. Finish session
    try {
        await finishSession(sessionServerId)
        await db.sessions.update(localSession.localId, { synced: true })
    } catch (cause) {
        throw new SyncError('Failed to finish session on server', 'finish', cause)
    }
}
