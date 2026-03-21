import { useState, useMemo } from 'react'
import { useQuery, useSuspenseQuery } from '@tanstack/react-query'
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    ReferenceLine,
    Area,
    ComposedChart,
} from 'recharts'
import { BarChart2 } from 'lucide-react'
import { loadHistoryQueryOptions } from '@/features/analytics/api'
import type { ChartPoint, TimeRange } from '@/features/analytics/types'
import { programsQueryOptions } from '@/features/programs/api'
import { api } from '@/shared/api/client'
import type { PaginatedResponse } from '@/shared/types/base'
import type { WorkoutDetail } from '@/features/workouts/types'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/shared/components/ui/select'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { cn } from '@/shared/utils/utils'

// ─── Time range config ────────────────────────────────────────────────────────

const TIME_RANGES: { value: TimeRange; label: string; days: number | null }[] = [
    { value: 'week', label: '7D', days: 7 },
    { value: 'month', label: '1M', days: 30 },
    { value: 'phase', label: 'Phase', days: null },
    { value: '3month', label: '3M', days: 90 },
    { value: 'year', label: '1Y', days: 365 },
]

// ─── Helpers ──────────────────────────────────────────────────────────────────

function TimeRangePills({
    value,
    onChange,
}: {
    value: TimeRange
    onChange: (v: TimeRange) => void
}) {
    return (
        <div className="flex items-center gap-1 bg-grey-900 border border-grey-800 rounded-lg p-1">
            {TIME_RANGES.map((r) => (
                <button
                    key={r.value}
                    type="button"
                    onClick={() => onChange(r.value)}
                    className={cn(
                        'px-3 py-1 rounded-md text-xs font-medium transition-colors cursor-pointer',
                        value === r.value
                            ? 'bg-brand-500/20 text-brand-300'
                            : 'text-grey-500 hover:text-grey-300',
                    )}
                >
                    {r.label}
                </button>
            ))}
        </div>
    )
}

function StatCard({ label, value, sub }: { label: string; value: string; sub?: string }) {
    return (
        <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 py-3">
            <p className="text-xs text-grey-500 mb-1">{label}</p>
            <p className="text-xl font-semibold text-grey-50">{value}</p>
            {sub && <p className="text-xs text-grey-600 mt-0.5">{sub}</p>}
        </div>
    )
}

function ChartTooltip({ active, payload, label }: any) {
    if (!active || !payload?.length) return null
    return (
        <div className="bg-grey-800 border border-grey-700 rounded-lg px-3 py-2.5 text-xs shadow-lg">
            <p className="text-grey-400 mb-1.5">{label}</p>
            {payload.map((entry: any) => (
                <div key={entry.name} className="flex items-center gap-2 py-0.5">
                    <span
                        className="w-2 h-2 rounded-full shrink-0"
                        style={{ backgroundColor: entry.color }}
                    />
                    <span className="text-grey-400">{entry.name}:</span>
                    <span className="text-grey-100 font-medium">
                        {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value}
                        {entry.name.toLowerCase().includes('load') ? '' : ' kg'}
                    </span>
                </div>
            ))}
        </div>
    )
}

// ─── Exercise Analytics ───────────────────────────────────────────────────────

export function ExerciseAnalytics() {
    const [selectedProgramId, setSelectedProgramId] = useState('')
    const [selectedExerciseId, setSelectedExerciseId] = useState('')
    const [timeRange, setTimeRange] = useState<TimeRange>('month')

    // All programs for the selector
    const { data: programsData } = useSuspenseQuery(programsQueryOptions())
    const programs = programsData.results
    const activeProgramId = selectedProgramId || programs[0]?.id || ''
    const activeProgram = programs.find((p) => p.id === activeProgramId) ?? null

    // Fetch all workouts for this program across all its phases, then
    // fetch each workout's detail to extract the exercise list.
    // We use the remaining_phases from the program list item to build phase IDs.
    const phaseIds = activeProgram?.remaining_phases.map((p) => p.id) ?? []

    const { data: phaseWorkouts } = useQuery({
        queryKey: ['analytics', 'phase-workouts', activeProgramId],
        queryFn: async () => {
            if (!phaseIds.length) return []
            const results = await Promise.all(
                phaseIds.map((phaseId) =>
                    api.get<PaginatedResponse<{ id: string }>>('/workouts/workouts/', {
                        params: { program_phase: phaseId },
                    }),
                ),
            )
            return results.flatMap((r) => r.results)
        },
        enabled: !!activeProgramId && phaseIds.length > 0,
    })

    const { data: workoutDetails } = useQuery({
        queryKey: ['analytics', 'workout-details', activeProgramId],
        queryFn: async () => {
            if (!phaseWorkouts?.length) return []
            // Cap at 30 workouts to avoid hammering the API
            return Promise.all(
                phaseWorkouts
                    .slice(0, 30)
                    .map((w) => api.get<WorkoutDetail>(`/workouts/workouts/${w.id}/`)),
            )
        },
        enabled: !!phaseWorkouts?.length,
    })

    // Unique exercises across all workouts
    const exercisePicker = useMemo(() => {
        if (!workoutDetails?.length) return []
        const seen = new Map<string, string>()
        workoutDetails.forEach((workout) => {
            workout.exercises?.forEach((ex) => {
                if (!seen.has(ex.exercise.id)) {
                    seen.set(ex.exercise.id, ex.exercise.exercise_name)
                }
            })
        })
        return Array.from(seen.entries())
            .map(([id, name]) => ({ id, name }))
            .sort((a, b) => a.name.localeCompare(b.name))
    }, [workoutDetails])

    // Load history for selected exercise
    const { data: history = [], isLoading: loadingHistory } = useQuery({
        ...loadHistoryQueryOptions(activeProgramId, selectedExerciseId),
        enabled: !!activeProgramId && !!selectedExerciseId,
    })

    // Map to chart points
    const allPoints: ChartPoint[] = useMemo(
        () =>
            history.map((entry) => ({
                date: new Date(entry.completed_at).toLocaleDateString('en-IE', {
                    day: 'numeric',
                    month: 'short',
                }),
                rawDate: new Date(entry.completed_at),
                oneRepMax: parseFloat(entry.one_rep_max),
                sessionLoad: parseFloat(entry.session_load),
                targetLoad: entry.target_load ? parseFloat(entry.target_load) : null,
                weightFloor: entry.weight_floor ? parseFloat(entry.weight_floor) : null,
                weightCeiling: entry.weight_ceiling ? parseFloat(entry.weight_ceiling) : null,
            })),
        [history],
    )

    // Filter by time range
    const filteredPoints = useMemo(() => {
        if (!allPoints.length) return []

        if (timeRange === 'phase' && activeProgram?.planned_start_date) {
            const start = new Date(activeProgram.planned_start_date)
            const end = activeProgram.planned_end_date
                ? new Date(activeProgram.planned_end_date)
                : new Date()
            return allPoints.filter((p) => p.rawDate >= start && p.rawDate <= end)
        }

        const range = TIME_RANGES.find((r) => r.value === timeRange)
        if (!range?.days) return allPoints
        const cutoff = new Date()
        cutoff.setDate(cutoff.getDate() - range.days)
        return allPoints.filter((p) => p.rawDate >= cutoff)
    }, [allPoints, timeRange, activeProgram])

    // Summary stats
    const stats = useMemo(() => {
        if (!filteredPoints.length) return null
        const latest = filteredPoints[filteredPoints.length - 1]
        const first = filteredPoints[0]
        return {
            latest,
            oneRepMaxChange: latest.oneRepMax - first.oneRepMax,
            maxLoad: Math.max(...filteredPoints.map((p) => p.sessionLoad)),
        }
    }, [filteredPoints])

    const hasWeightBand = filteredPoints.some((p) => p.weightFloor !== null)
    const hasTargetLoad = filteredPoints.some((p) => p.targetLoad !== null)

    const xAxisProps = {
        dataKey: 'date' as const,
        tick: { fill: '#6b7280', fontSize: 11 },
        tickLine: false,
        axisLine: false,
        interval: 'preserveStartEnd' as const,
    }
    const yAxisProps = {
        tick: { fill: '#6b7280', fontSize: 11 },
        tickLine: false,
        axisLine: false,
        width: 52,
    }
    const gridProps = {
        strokeDasharray: '3 3',
        stroke: 'rgba(255,255,255,0.05)',
        vertical: false,
    }

    return (
        <div className="p-8 max-w-5xl">
            {/* Header */}
            <div className="flex items-center gap-3 mb-8">
                <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400">
                    <BarChart2 size={18} />
                </div>
                <div>
                    <h1 className="text-2xl font-semibold text-grey-50">Analytics</h1>
                    <p className="text-sm text-grey-400 mt-0.5">
                        Exercise load and 1RM progression
                    </p>
                </div>
            </div>

            {/* Selectors */}
            <div className="flex flex-wrap gap-3 mb-6">
                <Select
                    value={activeProgramId}
                    onValueChange={(v) => {
                        setSelectedProgramId(v)
                        setSelectedExerciseId('')
                    }}
                >
                    <SelectTrigger className="bg-grey-900 border-grey-800 text-grey-200 w-60">
                        <SelectValue placeholder="Select program…" />
                    </SelectTrigger>
                    <SelectContent className="bg-grey-800 border-grey-700">
                        {programs.map((p) => (
                            <SelectItem
                                key={p.id}
                                value={p.id}
                                className="text-grey-100 focus:bg-grey-700"
                            >
                                {p.program_name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>

                <Select
                    value={selectedExerciseId}
                    onValueChange={setSelectedExerciseId}
                    disabled={!exercisePicker.length}
                >
                    <SelectTrigger className="bg-grey-900 border-grey-800 text-grey-200 w-60">
                        <SelectValue
                            placeholder={
                                exercisePicker.length ? 'Select exercise…' : 'No exercises yet'
                            }
                        />
                    </SelectTrigger>
                    <SelectContent className="bg-grey-800 border-grey-700">
                        {exercisePicker.map((ex) => (
                            <SelectItem
                                key={ex.id}
                                value={ex.id}
                                className="text-grey-100 focus:bg-grey-700"
                            >
                                {ex.name}
                            </SelectItem>
                        ))}
                    </SelectContent>
                </Select>
            </div>

            {/* States */}
            {!selectedExerciseId ? (
                <Empty className="border border-dashed border-grey-800 mt-4">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <BarChart2 />
                        </EmptyMedia>
                        <EmptyTitle className="text-sm text-grey-300">
                            Select an exercise
                        </EmptyTitle>
                        <EmptyDescription className="text-xs">
                            Choose a program and exercise to view load history and 1RM progression.
                        </EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : loadingHistory ? (
                <div className="flex items-center justify-center py-24">
                    <div className="size-6 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
                </div>
            ) : filteredPoints.length === 0 ? (
                <Empty className="border border-dashed border-grey-800 mt-4">
                    <EmptyHeader>
                        <EmptyMedia variant="icon">
                            <BarChart2 />
                        </EmptyMedia>
                        <EmptyTitle className="text-sm text-grey-300">No data yet</EmptyTitle>
                        <EmptyDescription className="text-xs">
                            Data appears here once the client completes workouts with this exercise.
                        </EmptyDescription>
                    </EmptyHeader>
                </Empty>
            ) : (
                <>
                    {/* Time range + count */}
                    <div className="flex items-center justify-between gap-4 mb-6">
                        <TimeRangePills value={timeRange} onChange={setTimeRange} />
                        <p className="text-xs text-grey-600">
                            {filteredPoints.length} session{filteredPoints.length !== 1 ? 's' : ''}
                        </p>
                    </div>

                    {/* Stats */}
                    {stats && (
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                            <StatCard
                                label="Current 1RM"
                                value={`${stats.latest.oneRepMax.toFixed(1)} kg`}
                            />
                            <StatCard
                                label="1RM Change"
                                value={`${stats.oneRepMaxChange >= 0 ? '+' : ''}${stats.oneRepMaxChange.toFixed(1)} kg`}
                                sub="vs window start"
                            />
                            <StatCard
                                label="Last Session Load"
                                value={stats.latest.sessionLoad.toFixed(0)}
                                sub="kg · reps"
                            />
                            <StatCard
                                label="Peak Load"
                                value={stats.maxLoad.toFixed(0)}
                                sub="kg · reps"
                            />
                        </div>
                    )}

                    {/* 1RM Chart */}
                    <div className="bg-grey-900 border border-grey-800 rounded-xl p-5 mb-4">
                        <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-5">
                            Estimated 1RM
                        </p>
                        <ResponsiveContainer width="100%" height={220}>
                            <LineChart
                                data={filteredPoints}
                                margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid {...gridProps} />
                                <XAxis {...xAxisProps} />
                                <YAxis {...yAxisProps} tickFormatter={(v) => `${v}kg`} />
                                <Tooltip content={<ChartTooltip />} />
                                <Line
                                    type="monotone"
                                    dataKey="oneRepMax"
                                    name="1RM"
                                    stroke="#818cf8"
                                    strokeWidth={2.5}
                                    dot={{ r: 3.5, fill: '#818cf8', strokeWidth: 0 }}
                                    activeDot={{ r: 5, fill: '#818cf8' }}
                                />
                                {hasWeightBand && (
                                    <>
                                        <Line
                                            type="monotone"
                                            dataKey="weightCeiling"
                                            name="Ceiling"
                                            stroke="#374151"
                                            strokeWidth={1}
                                            strokeDasharray="4 2"
                                            dot={false}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="weightFloor"
                                            name="Floor"
                                            stroke="#374151"
                                            strokeWidth={1}
                                            strokeDasharray="4 2"
                                            dot={false}
                                        />
                                    </>
                                )}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Session Load Chart */}
                    <div className="bg-grey-900 border border-grey-800 rounded-xl p-5">
                        <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-5">
                            Session Load (kg · reps)
                        </p>
                        <ResponsiveContainer width="100%" height={220}>
                            <ComposedChart
                                data={filteredPoints}
                                margin={{ top: 4, right: 8, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid {...gridProps} />
                                <XAxis {...xAxisProps} />
                                <YAxis {...yAxisProps} />
                                <Tooltip content={<ChartTooltip />} />
                                {stats?.latest.targetLoad && (
                                    <ReferenceLine
                                        y={stats.latest.targetLoad}
                                        stroke="#4b5563"
                                        strokeDasharray="4 2"
                                        label={{
                                            value: 'Target',
                                            fill: '#6b7280',
                                            fontSize: 10,
                                            position: 'insideTopRight',
                                        }}
                                    />
                                )}
                                <Area
                                    type="monotone"
                                    dataKey="sessionLoad"
                                    name="Session Load"
                                    stroke="#34d399"
                                    strokeWidth={2.5}
                                    fill="rgba(52,211,153,0.08)"
                                    dot={{ r: 3.5, fill: '#34d399', strokeWidth: 0 }}
                                    activeDot={{ r: 5, fill: '#34d399' }}
                                />
                                {hasTargetLoad && (
                                    <Line
                                        type="monotone"
                                        dataKey="targetLoad"
                                        name="Target Load"
                                        stroke="#4b5563"
                                        strokeWidth={1.5}
                                        strokeDasharray="4 2"
                                        dot={false}
                                    />
                                )}
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </>
            )}
        </div>
    )
}
