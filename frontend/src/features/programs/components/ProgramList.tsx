import { useSuspenseQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import { BookOpen, ChevronRight, Plus } from 'lucide-react'
import { programsQueryOptions } from '@/features/programs/api'
import type { ProgramListItem, ProgramStatusCode } from '@/features/programs/types'
import { Badge } from '@/shared/components/ui/badge'
import { Button } from '@/shared/components/ui/button'
import {
    Empty,
    EmptyHeader,
    EmptyMedia,
    EmptyTitle,
    EmptyDescription,
} from '@/shared/components/ui/empty'
import { Separator } from '@/shared/components/ui/separator'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'
import { CreateProgramSheet } from './CreateProgramSheet'

// ─── Status config ────────────────────────────────────────────────────────────

const STATUS_STYLES: Record<ProgramStatusCode, string> = {
    CREATING: 'bg-grey-700/40 text-grey-400 border-transparent',
    OUT_FOR_REVIEW: 'bg-info-500/10 text-info-400 border-transparent',
    READY_TO_BEGIN: 'bg-warning-500/10 text-warning-400 border-transparent',
    IN_PROGRESS: 'bg-success-500/10 text-success-400 border-transparent',
    COMPLETED: 'bg-brand-500/10 text-brand-400 border-transparent',
    ABANDONED: 'bg-danger-500/10 text-danger-400 border-transparent',
}

const STATUS_LABELS: Record<ProgramStatusCode, string> = {
    CREATING: 'Draft',
    OUT_FOR_REVIEW: 'In Review',
    READY_TO_BEGIN: 'Ready',
    IN_PROGRESS: 'In Progress',
    COMPLETED: 'Completed',
    ABANDONED: 'Abandoned',
}

// ─── Status normaliser ────────────────────────────────────────────────────────
const LABEL_TO_CODE: Record<string, ProgramStatusCode> = {
    Creating: 'CREATING',
    'Out for Review': 'OUT_FOR_REVIEW',
    'Ready to Begin': 'READY_TO_BEGIN',
    'In Progress': 'IN_PROGRESS',
    Completed: 'COMPLETED',
    Abandoned: 'ABANDONED',
}

function getStatusCode(status: { code?: ProgramStatusCode; label: string }): ProgramStatusCode {
    return status.code ?? LABEL_TO_CODE[status.label] ?? 'CREATING'
}

// ─── Program Row ──────────────────────────────────────────────────────────────

function ProgramRow({ program }: { program: ProgramListItem }) {
    const navigate = useNavigate()
    const statusStyle = STATUS_STYLES[getStatusCode(program.status)] ?? STATUS_STYLES.CREATING
    const statusLabel = STATUS_LABELS[getStatusCode(program.status)] ?? program.status.label

    const dateRange =
        program.planned_start_date && program.planned_end_date
            ? `${new Date(program.planned_start_date).toLocaleDateString('en-IE', { day: 'numeric', month: 'short' })} — ${new Date(program.planned_end_date).toLocaleDateString('en-IE', { day: 'numeric', month: 'short', year: 'numeric' })}`
            : null

    return (
        <Button
            variant="outline"
            onClick={() => navigate({ to: `${ROUTES.trainer.programs}/${program.id}` })}
            className="h-auto w-full justify-start gap-4 px-4 py-3 text-left"
        >
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-400 shrink-0">
                <BookOpen size={15} />
            </div>

            <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-grey-100 truncate">{program.program_name}</p>
                <p className="text-xs text-grey-500 mt-0.5">
                    {program.training_goal.label} · {program.experience_level.label}
                    {dateRange && ` · ${dateRange}`}
                </p>
            </div>

            <div className="flex items-center gap-3 shrink-0">
                {program.has_created_phases && (
                    <span className="text-xs text-grey-500">
                        {program.remaining_phases.length} phase
                        {program.remaining_phases.length !== 1 ? 's' : ''} left
                    </span>
                )}
                <Badge className={cn('h-5', statusStyle)}>{statusLabel}</Badge>
                <ChevronRight size={15} className="text-grey-600" />
            </div>
        </Button>
    )
}

// ─── Empty state ──────────────────────────────────────────────────────────────

function EmptyPrograms({ onNew }: { onNew: () => void }) {
    return (
        <Empty className="border border-dashed border-grey-800">
            <EmptyHeader>
                <EmptyMedia variant="icon">
                    <BookOpen />
                </EmptyMedia>
                <EmptyTitle className="text-sm text-grey-300">No programs yet</EmptyTitle>
                <EmptyDescription className="text-xs">
                    Create your first program for a client to get started.
                </EmptyDescription>
            </EmptyHeader>
            <Button size="sm" onClick={onNew} className="gap-1.5">
                <Plus size={13} />
                New Program
            </Button>
        </Empty>
    )
}

// ─── Group ────────────────────────────────────────────────────────────────────

function ProgramGroup({ title, programs }: { title: string; programs: ProgramListItem[] }) {
    if (programs.length === 0) return null
    return (
        <div>
            <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-3">
                {title}
            </p>
            <div className="flex flex-col gap-2">
                {programs.map((p) => (
                    <ProgramRow key={p.id} program={p} />
                ))}
            </div>
        </div>
    )
}

// ─── Program List ─────────────────────────────────────────────────────────────

export function ProgramList() {
    const [sheetOpen, setSheetOpen] = useState(false)
    const { data: programs } = useSuspenseQuery(programsQueryOptions())

    const active = programs.results.filter((p) => ['IN_PROGRESS'].includes(getStatusCode(p.status)))
    const pending = programs.results.filter((p) =>
        ['CREATING', 'OUT_FOR_REVIEW', 'READY_TO_BEGIN'].includes(getStatusCode(p.status)),
    )
    const finished = programs.results.filter((p) =>
        ['COMPLETED', 'ABANDONED'].includes(getStatusCode(p.status)),
    )

    return (
        <>
            <div className="p-8 max-w-3xl">
                <div className="flex items-center justify-between gap-4 mb-8">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400">
                            <BookOpen size={18} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-semibold text-grey-50">Programs</h1>
                            <p className="text-sm text-grey-400 mt-0.5">
                                {programs.count} {programs.count === 1 ? 'program' : 'programs'}{' '}
                                total
                            </p>
                        </div>
                    </div>
                    <Button
                        size="sm"
                        onClick={() => setSheetOpen(true)}
                        className="gap-1.5 shrink-0"
                    >
                        <Plus size={13} />
                        New Program
                    </Button>
                </div>

                {programs.count === 0 ? (
                    <EmptyPrograms onNew={() => setSheetOpen(true)} />
                ) : (
                    <div className="flex flex-col gap-8">
                        <ProgramGroup title="Active" programs={active} />
                        {active.length > 0 && pending.length > 0 && (
                            <Separator className="bg-grey-800" />
                        )}
                        <ProgramGroup title="Pending" programs={pending} />
                        {(active.length > 0 || pending.length > 0) && finished.length > 0 && (
                            <Separator className="bg-grey-800" />
                        )}
                        <ProgramGroup title="Finished" programs={finished} />
                    </div>
                )}
            </div>

            <CreateProgramSheet open={sheetOpen} onOpenChange={setSheetOpen} />
        </>
    )
}
