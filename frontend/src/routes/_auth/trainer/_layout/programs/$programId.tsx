import { createFileRoute } from '@tanstack/react-router'
import { ProgramDetail } from '@/features/programs/components/ProgramDetail'
import { programDetailQueryOptions } from '@/features/programs/api'

export const Route = createFileRoute('/_auth/trainer/_layout/programs/$programId')({
    loader: ({ context: { queryClient }, params: { programId } }) =>
        queryClient.ensureQueryData(programDetailQueryOptions(programId)),

    component: function ProgramDetailRoute() {
        const { programId } = Route.useParams()
        return <ProgramDetail programId={programId} />
    },
})
