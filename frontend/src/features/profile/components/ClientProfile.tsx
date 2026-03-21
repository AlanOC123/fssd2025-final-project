import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Mail, User, Edit2, Check, X } from 'lucide-react'
import { authApi } from '@/features/auth/api'
import { clientProfileApi, CLIENT_PROFILE_QUERY_KEY } from '@/features/profile/api'
import { useAuthStore } from '@/features/auth/store'
import { AUTH_QUERY_KEY } from '@/features/auth/hooks/useAuthQuery'
import { useAuth } from '@/shared/hooks/useAuth'
import { api } from '@/shared/api/client'
import type { PaginatedResponse, LabelLookup } from '@/shared/types/base'
import type { ClientProfile as ClientProfileType } from '@/features/auth/types'
import { AvatarUpload } from '@/shared/components/ui/AvatarUpload'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { Separator } from '@/shared/components/ui/separator'
import { Badge } from '@/shared/components/ui/badge'
import { toast, toastApiError } from '@/shared/utils/toast'
import { cn } from '@/shared/utils/utils'

// ─── Editable Name + Avatar ───────────────────────────────────────────────────

function EditableName() {
    const { user } = useAuth()
    const setUser = useAuthStore((s) => s.setUser)
    const queryClient = useQueryClient()
    const [editing, setEditing] = useState(false)
    const [firstName, setFirstName] = useState(user?.first_name ?? '')
    const [lastName, setLastName] = useState(user?.last_name ?? '')

    const nameMutation = useMutation({
        mutationFn: () => authApi.updateUser({ first_name: firstName, last_name: lastName }),
        onSuccess: (updatedUser) => {
            setUser(updatedUser)
            queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
            setEditing(false)
            toast.success('Name updated')
        },
        onError: (error) => toastApiError(error, 'Failed to update name'),
    })

    const avatarMutation = useMutation({
        mutationFn: (file: File) => clientProfileApi.updateAvatar(file),
        onSuccess: () => {
            // Re-fetch user so profile.avatar updates in the store
            authApi.getUser().then((u) => {
                setUser(u)
                queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
                queryClient.invalidateQueries({ queryKey: CLIENT_PROFILE_QUERY_KEY })
            })
            toast.success('Avatar updated')
        },
        onError: (error) => toastApiError(error, 'Failed to upload avatar'),
    })

    const handleCancel = () => {
        setFirstName(user?.first_name ?? '')
        setLastName(user?.last_name ?? '')
        setEditing(false)
    }

    const profile = user?.profile as ClientProfileType | null
    const avatarSrc = profile?.avatar || null
    const initials =
        `${user?.first_name?.[0] ?? ''}${user?.last_name?.[0] ?? ''}`.toUpperCase() || '?'

    return (
        <div className="flex items-center gap-4">
            <AvatarUpload
                src={avatarSrc}
                initials={initials}
                onFileSelected={(file: File) => avatarMutation.mutate(file)}
                isUploading={avatarMutation.isPending}
            />

            <div className="flex-1 min-w-0">
                {editing ? (
                    <div className="flex flex-col gap-2">
                        <div className="flex gap-2">
                            <div className="flex-1">
                                <Label
                                    htmlFor="first-name"
                                    className="text-xs text-grey-500 mb-1 block"
                                >
                                    First name
                                </Label>
                                <Input
                                    id="first-name"
                                    value={firstName}
                                    onChange={(e) => setFirstName(e.target.value)}
                                    className="h-8 text-sm"
                                    autoFocus
                                />
                            </div>
                            <div className="flex-1">
                                <Label
                                    htmlFor="last-name"
                                    className="text-xs text-grey-500 mb-1 block"
                                >
                                    Last name
                                </Label>
                                <Input
                                    id="last-name"
                                    value={lastName}
                                    onChange={(e) => setLastName(e.target.value)}
                                    className="h-8 text-sm"
                                />
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <Button
                                size="sm"
                                onClick={() => nameMutation.mutate()}
                                disabled={nameMutation.isPending || !firstName.trim()}
                                className="gap-1.5"
                            >
                                <Check size={13} />
                                {nameMutation.isPending ? 'Saving…' : 'Save'}
                            </Button>
                            <Button
                                size="sm"
                                variant="ghost"
                                onClick={handleCancel}
                                disabled={nameMutation.isPending}
                                className="gap-1.5 text-grey-400"
                            >
                                <X size={13} />
                                Cancel
                            </Button>
                        </div>
                    </div>
                ) : (
                    <div className="flex items-center gap-2">
                        <div>
                            <p className="text-lg font-semibold text-grey-50">{user?.full_name}</p>
                            <p className="text-xs text-grey-500 mt-0.5">Athlete</p>
                        </div>
                        <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => setEditing(true)}
                            className="text-grey-600 hover:text-grey-300 ml-1"
                            aria-label="Edit name"
                        >
                            <Edit2 size={13} />
                        </Button>
                    </div>
                )}
            </div>
        </div>
    )
}

// ─── Editable Training Profile ─────────────────────────────────────────────────

function EditableTrainingProfile() {
    const { user } = useAuth()
    const setUser = useAuthStore((s) => s.setUser)
    const queryClient = useQueryClient()
    const [editing, setEditing] = useState(false)

    const profile = user?.profile as ClientProfileType | null
    const [selectedGoalId, setSelectedGoalId] = useState<string>(profile?.goal?.id ?? '')
    const [selectedLevelId, setSelectedLevelId] = useState<string>(profile?.level?.id ?? '')

    const { data: goalsData } = useQuery({
        queryKey: ['training-goals'],
        queryFn: () => api.get<PaginatedResponse<LabelLookup>>('/users/training-goals/'),
        enabled: editing,
    })
    const { data: levelsData } = useQuery({
        queryKey: ['experience-levels'],
        queryFn: () => api.get<PaginatedResponse<LabelLookup>>('/users/experience-levels/'),
        enabled: editing,
    })

    const goals = goalsData?.results ?? []
    const levels = levelsData?.results ?? []

    const mutation = useMutation({
        mutationFn: () =>
            clientProfileApi.update({
                goal_id: selectedGoalId || null,
                level_id: selectedLevelId || null,
            }),
        onSuccess: () => {
            // Re-fetch user so profile updates in auth store
            authApi.getUser().then((u) => {
                setUser(u)
                queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
            })
            setEditing(false)
            toast.success('Training profile updated')
        },
        onError: (error) => toastApiError(error, 'Failed to update training profile'),
    })

    const handleCancel = () => {
        setSelectedGoalId(profile?.goal?.id ?? '')
        setSelectedLevelId(profile?.level?.id ?? '')
        setEditing(false)
    }

    if (editing) {
        return (
            <div className="py-3 flex flex-col gap-4">
                <div>
                    <p className="text-xs text-grey-500 mb-2">Training Goal</p>
                    <div className="flex flex-wrap gap-2">
                        {goals.map((g) => (
                            <button
                                key={g.id}
                                type="button"
                                onClick={() => setSelectedGoalId(g.id)}
                                className={cn(
                                    'px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer',
                                    selectedGoalId === g.id
                                        ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                                        : 'bg-grey-800 text-grey-500 border-grey-700 hover:border-grey-600',
                                )}
                            >
                                {g.label}
                            </button>
                        ))}
                    </div>
                </div>
                <div>
                    <p className="text-xs text-grey-500 mb-2">Experience Level</p>
                    <div className="flex flex-wrap gap-2">
                        {levels.map((l) => (
                            <button
                                key={l.id}
                                type="button"
                                onClick={() => setSelectedLevelId(l.id)}
                                className={cn(
                                    'px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer',
                                    selectedLevelId === l.id
                                        ? 'bg-grey-600/40 text-grey-200 border-grey-500/40'
                                        : 'bg-grey-800 text-grey-500 border-grey-700 hover:border-grey-600',
                                )}
                            >
                                {l.label}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="flex gap-2">
                    <Button
                        size="sm"
                        onClick={() => mutation.mutate()}
                        disabled={mutation.isPending}
                        className="gap-1.5"
                    >
                        <Check size={13} />
                        {mutation.isPending ? 'Saving…' : 'Save'}
                    </Button>
                    <Button
                        size="sm"
                        variant="ghost"
                        onClick={handleCancel}
                        disabled={mutation.isPending}
                        className="gap-1.5 text-grey-400"
                    >
                        <X size={13} />
                        Cancel
                    </Button>
                </div>
            </div>
        )
    }

    return (
        <div className="py-2">
            <div className="flex items-center justify-between py-1">
                <p className="text-xs font-medium text-grey-500 uppercase tracking-wider">
                    Training Profile
                </p>
                <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setEditing(true)}
                    className="text-grey-600 hover:text-grey-300"
                    aria-label="Edit training profile"
                >
                    <Edit2 size={13} />
                </Button>
            </div>
            <Separator className="bg-grey-800 my-2" />
            <div className="flex flex-col gap-3 py-1">
                <div>
                    <p className="text-xs text-grey-500 mb-1.5">Training goal</p>
                    {profile?.goal ? (
                        <Badge className="bg-brand-500/10 text-brand-400 border-transparent">
                            {profile.goal.label}
                        </Badge>
                    ) : (
                        <button
                            type="button"
                            onClick={() => setEditing(true)}
                            className="text-sm text-grey-600 hover:text-brand-400 transition-colors"
                        >
                            Set your training goal →
                        </button>
                    )}
                </div>
                <div>
                    <p className="text-xs text-grey-500 mb-1.5">Experience level</p>
                    {profile?.level ? (
                        <Badge className="bg-grey-700/40 text-grey-400 border-transparent">
                            {profile.level.label}
                        </Badge>
                    ) : (
                        <button
                            type="button"
                            onClick={() => setEditing(true)}
                            className="text-sm text-grey-600 hover:text-brand-400 transition-colors"
                        >
                            Set your experience level →
                        </button>
                    )}
                </div>
            </div>
            {(!profile?.goal || !profile?.level) && (
                <p className="text-xs text-warning-400 bg-warning-500/10 border border-warning-500/20 rounded-lg px-3 py-2 mt-2">
                    Set your goal and level so trainers can find and match with you.
                </p>
            )}
        </div>
    )
}

// ─── Client Profile ───────────────────────────────────────────────────────────

export function ClientProfile() {
    const { user } = useAuth()

    return (
        <div className="p-6 max-w-2xl mx-auto">
            <h1 className="text-2xl font-semibold text-grey-50 mb-8">Profile</h1>

            {/* Avatar + Name */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 py-4 mb-4">
                <EditableName />
            </div>

            {/* Account info */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 mb-4">
                <div className="flex items-center gap-4 py-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-500 shrink-0">
                        <Mail size={15} />
                    </div>
                    <div>
                        <p className="text-xs text-grey-500">Email</p>
                        <p className="text-sm font-medium text-grey-100 mt-0.5">
                            {user?.email ?? ''}
                        </p>
                    </div>
                </div>
                <Separator className="bg-grey-800" />
                <div className="flex items-center gap-4 py-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-500 shrink-0">
                        <User size={15} />
                    </div>
                    <div>
                        <p className="text-xs text-grey-500">Account type</p>
                        <p className="text-sm font-medium text-grey-100 mt-0.5">Athlete</p>
                    </div>
                </div>
            </div>

            {/* Training profile — editable */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 mb-4">
                <EditableTrainingProfile />
            </div>
        </div>
    )
}
