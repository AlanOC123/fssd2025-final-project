import { createFileRoute } from '@tanstack/react-router'
import { ProgramList } from '@/features/programs/components/ProgramList'
import { programsQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/programs/')({
    loader: ({ context: { queryClient } }) => queryClient.ensureQueryData(programsQueryOptions()),

    component: ProgramList,
})
