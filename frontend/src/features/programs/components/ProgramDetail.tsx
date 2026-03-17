import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import {
    ArrowLeft,
    Calendar,
    Clock,
    CheckCircle,
    SkipForward,
    Archive,
    BookOpen,
} from 'lucide-react'
import { programDetailQueryOptions } from '@/features/programs/api'
import type { ProgramPhase, PhaseStatusCode } from '@/features/programs/types'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import { Separator } from '@/shared/components/ui/separator'
import { Empty, EmptyHeader, EmptyMedia, EmptyTitle } from '@/shared/components/ui/empty'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'

// ─── Status config ────────────────────────────────────────────────────────────

const PHASE_STATUS_CONFIG: Record<
    PhaseStatusCode,
    { label: string; className: string; icon: React.ElementType }
> = {
    PLANNED: {
        label: 'Planned',
        className: 'bg-grey-700/40 text-grey-400 border-transparent',
        icon: Clock,
    },
    NEXT: {
        label: 'Next',
        className: 'bg-warning-500/10 text-warning-400 border-transparent',
        icon: Clock,
    },
    ACTIVE: {
        label: 'Active',
        className: 'bg-success-500/10 text-success-400 border-transparent',
        icon: Clock,
    },
    COMPLETED: {
        label: 'Completed',
        className: 'bg-brand-500/10 text-brand-400 border-transparent',
        icon: CheckCircle,
    },
    SKIPPED: {
        label: 'Skipped',
        className: 'bg-grey-700/40 text-grey-500 border-transparent',
        icon: SkipForward,
    },
    ARCHIVED: {
        label: 'Archived',
        className: 'bg-grey-700/40 text-grey-500 border-transparent',
        icon: Archive,
    },
}

const PROGRAM_STATUS_STYLES: Record<string, string> = {
    CREATING: 'bg-grey-700/40 text-grey-400 border-transparent',
    OUT_FOR_REVIEW: 'bg-info-500/10 text-info-400 border-transparent',
    READY_TO_BEGIN: 'bg-warning-500/10 text-warning-400 border-transparent',
    IN_PROGRESS: 'bg-success-500/10 text-success-400 border-transparent',
    COMPLETED: 'bg-brand-500/10 text-brand-400 border-transparent',
    ABANDONED: 'bg-danger-500/10 text-danger-400 border-transparent',
}

// ─── Phase Row ────────────────────────────────────────────────────────────────

function PhaseRow({ phase }: { phase: ProgramPhase }) {
    const config = PHASE_STATUS_CONFIG[phase.status.code] ?? PHASE_STATUS_CONFIG.PLANNED
    const isFinished = ['COMPLETED', 'SKIPPED', 'ARCHIVED'].includes(phase.status.code)

    const dateRange = `${new Date(phase.planned_start_date).toLocaleDateString('en-IE', {
        day: 'numeric',
        month: 'short',
    })} — ${new Date(phase.planned_end_date).toLocaleDateString('en-IE', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
    })}`

    return (
        <div
            className={cn(
                'flex items-start gap-4 px-4 py-3 rounded-lg border border-grey-800',
                isFinished ? 'bg-grey-900/50 opacity-60' : 'bg-grey-900',
            )}
        >
            <div className="flex items-center justify-center w-6 h-6 rounded-full bg-grey-800 text-grey-500 text-xs font-medium shrink-0 mt-0.5">
                {phase.sequence_order}
            </div>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100">
                    {phase.phase_name || phase.phase_option.label}
                </p>
                {phase.phase_goal && (
                    <p className="text-xs text-grey-400 mt-0.5">{phase.phase_goal}</p>
                )}
                <div className="flex items-center gap-1.5 mt-1 text-xs text-grey-500">
                    <Calendar size={11} />
                    <span>{dateRange}</span>
                    <span className="text-grey-700">·</span>
                    <span>{phase.duration_weeks}w</span>
                </div>
            </div>

            <Badge className={cn('h-5 mt-0.5', config.className)}>{config.label}</Badge>
        </div>
    )
}

// ─── Notes block ─────────────────────────────────────────────────────────────

function NotesBlock({ title, content }: { title: string; content: string }) {
    if (!content) return null
    return (
        <div>
            <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-2">
                {title}
            </p>
            <p className="text-sm text-grey-400 bg-grey-900 border border-grey-800 rounded-lg px-4 py-3">
                {content}
            </p>
        </div>
    )
}

// ─── Program Detail ───────────────────────────────────────────────────────────

export function ProgramDetail({ programId }: { programId: string }) {
    const navigate = useNavigate()
    const { data: program } = useSuspenseQuery(programDetailQueryOptions(programId))

    const statusStyle = PROGRAM_STATUS_STYLES[program.status.code] ?? PROGRAM_STATUS_STYLES.CREATING

    const dateRange =
        program.planned_start_date && program.planned_end_date
            ? `${new Date(program.planned_start_date).toLocaleDateString('en-IE', { day: 'numeric', month: 'short' })} — ${new Date(program.planned_end_date).toLocaleDateString('en-IE', { day: 'numeric', month: 'short', year: 'numeric' })}`
            : null

    const hasNotes = program.review_notes || program.completion_notes || program.abandonment_reason

    return (
        <div className="p-8 max-w-3xl">
            {/* Back */}
            <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate({ to: ROUTES.trainer.programs })}
                className="mb-6 -ml-2 text-grey-500 hover:text-grey-200"
            >
                <ArrowLeft size={15} />
                Programs
            </Button>

            {/* Header */}
            <div className="mb-8">
                <div className="flex items-start justify-between gap-4 mb-2">
                    <h1 className="text-2xl font-semibold text-grey-50">{program.program_name}</h1>
                    <Badge className={cn('mt-1 shrink-0', statusStyle)}>
                        {program.status.label}
                    </Badge>
                </div>

                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-grey-500">
                    <span>{program.training_goal.label}</span>
                    <span className="text-grey-700">·</span>
                    <span>{program.experience_level.label}</span>
                    {program.program_duration_weeks > 0 && (
                        <>
                            <span className="text-grey-700">·</span>
                            <span>{program.program_duration_weeks} weeks</span>
                        </>
                    )}
                    {dateRange && (
                        <>
                            <span className="text-grey-700">·</span>
                            <span className="flex items-center gap-1">
                                <Calendar size={11} />
                                {dateRange}
                            </span>
                        </>
                    )}
                </div>

                {program.has_created_phases && (
                    <div className="flex items-center gap-3 mt-3 text-xs text-grey-500">
                        <span>{program.phases.length} phases</span>
                        {program.number_of_completed_phases > 0 && (
                            <span className="text-brand-400">
                                {program.number_of_completed_phases} completed
                            </span>
                        )}
                        {program.number_of_skipped_phases > 0 && (
                            <span>{program.number_of_skipped_phases} skipped</span>
                        )}
                    </div>
                )}
            </div>

            <Separator className="bg-grey-800 mb-8" />

            {/* Phases */}
            <div className="mb-8">
                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                    Phases
                </p>
                {program.phases.length === 0 ? (
                    <Empty className="border border-dashed border-grey-800 py-8">
                        <EmptyHeader>
                            <EmptyMedia variant="icon">
                                <BookOpen />
                            </EmptyMedia>
                            <EmptyTitle className="text-sm text-grey-500">No phases yet</EmptyTitle>
                        </EmptyHeader>
                    </Empty>
                ) : (
                    <div className="flex flex-col gap-2">
                        {program.phases.map((phase) => (
                            <PhaseRow key={phase.id} phase={phase} />
                        ))}
                    </div>
                )}
            </div>

            {/* Notes */}
            {hasNotes && (
                <>
                    <Separator className="bg-grey-800 mb-8" />
                    <div className="flex flex-col gap-6">
                        <NotesBlock title="Review Notes" content={program.review_notes} />
                        <NotesBlock title="Completion Notes" content={program.completion_notes} />
                        <NotesBlock
                            title="Abandonment Reason"
                            content={program.abandonment_reason}
                        />
                    </div>
                </>
            )}
        </div>
    )
}
