import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle } from 'lucide-react'
import { membershipsApi, MEMBERSHIP_QUERY_KEY } from '@/features/memberships/api'
import { toast, toastApiError } from '@/shared/utils/toast'
import { Button } from '@/shared/components/ui/button'
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/shared/components/ui/dialog'

interface DissolveDialogProps {
    membershipId: string
    trainerName: string
    open: boolean
    onOpenChange: (open: boolean) => void
}

export function DissolveDialog({
    membershipId,
    trainerName,
    open,
    onOpenChange,
}: DissolveDialogProps) {
    const queryClient = useQueryClient()

    const dissolveMutation = useMutation({
        mutationFn: () => membershipsApi.dissolve(membershipId),
        onSuccess: () => {
            toast.success('Membership dissolved')
            queryClient.invalidateQueries({ queryKey: MEMBERSHIP_QUERY_KEY() })
            onOpenChange(false)
        },
        onError: (error) => toastApiError(error, 'Failed to dissolve membership'),
    })

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <div className="flex items-center gap-3 mb-1">
                        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-danger-500/10 text-danger-400 shrink-0">
                            <AlertTriangle size={18} />
                        </div>
                        <DialogTitle>Leave trainer?</DialogTitle>
                    </div>
                    <DialogDescription>
                        This will dissolve your membership with{' '}
                        <span className="text-grey-200 font-medium">{trainerName}</span>. Your
                        program history will be preserved but you won't receive new workouts until
                        you connect with a new trainer.
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button
                        variant="outline"
                        onClick={() => onOpenChange(false)}
                        disabled={dissolveMutation.isPending}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        onClick={() => dissolveMutation.mutate()}
                        disabled={dissolveMutation.isPending}
                    >
                        {dissolveMutation.isPending ? 'Leaving...' : 'Leave trainer'}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}
