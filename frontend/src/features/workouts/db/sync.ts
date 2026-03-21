import { api } from '@/shared/api/client'
import { db } from './schema'
import type { LocalSession, LocalExerciseRecord, LocalSetRecord } from './schema'
import { tryCatch } from '@/shared/utils/tryCatch'

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

const startSession = (workoutId: string): Promise<SessionResponse> =>
    api.post<SessionResponse>('/workouts/workout-sessions/start/', { workout_id: workoutId })

const finishSession = (serverId: string): Promise<SessionResponse> =>
    api.post<SessionResponse>(`/workouts/workout-sessions/${serverId}/finish/`)

const startExercise = (
    workoutExerciseId: string,
    sessionServerId: string,
): Promise<ExerciseRecordResponse> =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/start/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

const skipExercise = (
    workoutExerciseId: string,
    sessionServerId: string,
): Promise<ExerciseRecordResponse> =>
    api.post<ExerciseRecordResponse>('/workouts/exercise-records/skip/', {
        workout_exercise_id: workoutExerciseId,
        session_id: sessionServerId,
    })

const completeSet = (set: LocalSetRecord, exerciseServerId: string): Promise<SetRecordResponse> =>
    api.post<SetRecordResponse>('/workouts/set-records/complete/', {
        workout_set_id: set.workoutSetId,
        exercise_record_id: exerciseServerId,
        reps_completed: set.repsCompleted,
        weight_completed: set.weightCompleted,
        ...(set.difficultyRating != null && { difficulty_rating: set.difficultyRating }),
        ...(set.repsInReserve != null && { reps_in_reserve: set.repsInReserve }),
    })

const skipSet = (workoutSetId: string, exerciseServerId: string): Promise<SetRecordResponse> =>
    api.post<SetRecordResponse>('/workouts/set-records/skip/', {
        workout_set_id: workoutSetId,
        exercise_record_id: exerciseServerId,
    })

// ─── Sync Error ───────────────────────────────────────────────────────────────

export class SyncError extends Error {
    constructor(
        message: string,
        public readonly step: 'session' | 'exercise' | 'set' | 'finish',
        public readonly cause?: unknown,
    ) {
        super(message)
        this.name = 'SyncError'
    }
}

// ─── Sync ─────────────────────────────────────────────────────────────────────

export async function syncSession(localSession: LocalSession): Promise<void> {
    let sessionServerId: string

    if (localSession.serverId) {
        sessionServerId = localSession.serverId
    } else {
        const { data, error } = await tryCatch(startSession(localSession.workoutId))
        if (error) throw new SyncError('Failed to start session on server', 'session', error)
        sessionServerId = data.id
        await db.sessions.update(localSession.localId, { serverId: sessionServerId })
    }

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
                ? await tryCatch(skipExercise(exercise.workoutExerciseId, sessionServerId))
                : await tryCatch(startExercise(exercise.workoutExerciseId, sessionServerId))

            const { data, error } = exerciseRes
            if (error)
                throw new SyncError(
                    `Failed to sync exercise ${exercise.workoutExerciseId}`,
                    'exercise',
                    error,
                )

            exerciseServerId = data.id
            await db.exerciseRecords.update(exercise.localId, {
                serverId: exerciseServerId,
                synced: true,
            })
        }

        if (exercise.skipped) continue

        const setRecords: LocalSetRecord[] = await db.setRecords
            .where('localExerciseId')
            .equals(exercise.localId)
            .sortBy('completedAt')

        for (const set of setRecords) {
            // Skip if already synced
            if (set.synced) continue

            const setRes = set.skipped
                ? await tryCatch(skipSet(set.workoutSetId, exerciseServerId))
                : await tryCatch(completeSet(set, exerciseServerId))

            const { error } = setRes
            if (error) throw new SyncError(`Failed to sync set ${set.workoutSetId}`, 'set', error)

            await db.setRecords.update(set.localId, { synced: true })
        }
    }

    // 4. Finish session — skip if already done
    if (!localSession.synced) {
        const { error } = await tryCatch(finishSession(sessionServerId))
        if (error) throw new SyncError('Failed to finish session on server', 'finish', error)
        await db.sessions.update(localSession.localId, { synced: true })
    }
}
