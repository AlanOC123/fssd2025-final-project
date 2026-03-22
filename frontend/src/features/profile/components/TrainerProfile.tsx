import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Check, X, Edit2, Globe, Mail, User } from 'lucide-react'
import {
    trainerProfileApi,
    trainerProfileQueryOptions,
    TRAINER_PROFILE_QUERY_KEY,
} from '@/features/profile/api'
import { authApi } from '@/features/auth/api'
import { useAuthStore } from '@/features/auth/store'
import { AUTH_QUERY_KEY } from '@/features/auth/hooks/useAuthQuery'
import { useAuth } from '@/shared/hooks/useAuth'
import { api } from '@/shared/api/client'
import type { PaginatedResponse, LabelLookup } from '@/shared/types/base'
import type { TrainerProfile as TrainerProfileType } from '@/features/auth/types'
import { LogoUpload } from '@/shared/components/ui/LogoUpload'
import { Button } from '@/shared/components/ui/button'
import { Input } from '@/shared/components/ui/input'
import { Label } from '@/shared/components/ui/label'
import { Separator } from '@/shared/components/ui/separator'
import { Badge } from '@/shared/components/ui/badge'
import { toast, toastApiError } from '@/shared/utils/toast'
import { Avatar, AvatarFallback } from '@/shared/components/ui/avatar'

// ─── Editable Name ────────────────────────────────────────────────────────────

function EditableName() {
    const { user } = useAuth()
    const setUser = useAuthStore((s) => s.setUser)
    const queryClient = useQueryClient()
    const [editing, setEditing] = useState(false)
    const [firstName, setFirstName] = useState(user?.first_name ?? '')
    const [lastName, setLastName] = useState(user?.last_name ?? '')

    const mutation = useMutation({
        mutationFn: () => authApi.updateUser({ first_name: firstName, last_name: lastName }),
        onSuccess: (updatedUser) => {
            setUser(updatedUser)
            queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
            setEditing(false)
            toast.success('Name updated')
        },
        onError: (error) => toastApiError(error, 'Failed to update name'),
    })

    // Trainers don't have a personal avatar — logo upload is in EditableBusinessInfo

    const handleCancel = () => {
        setFirstName(user?.first_name ?? '')
        setLastName(user?.last_name ?? '')
        setEditing(false)
    }

    const initials =
        `${user?.first_name?.[0] ?? ''}${user?.last_name?.[0] ?? ''}`.toUpperCase() || '?'

    return (
        <div className="flex items-center gap-4">
            <Avatar size="lg" className="w-16 h-16 shrink-0">
                <AvatarFallback className="bg-brand-800 text-brand-200 text-xl font-semibold">
                    {initials}
                </AvatarFallback>
            </Avatar>

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
                                onClick={() => mutation.mutate()}
                                disabled={mutation.isPending || !firstName.trim()}
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
                ) : (
                    <div className="flex items-center gap-2">
                        <div>
                            <p className="text-lg font-semibold text-grey-50">{user?.full_name}</p>
                            <p className="text-xs text-grey-500 mt-0.5">Trainer</p>
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

// ─── Editable Business Info ───────────────────────────────────────────────────

function EditableBusinessInfo({ profile }: { profile: TrainerProfileType }) {
    const queryClient = useQueryClient()
    const setUser = useAuthStore((s) => s.setUser)
    const [editing, setEditing] = useState(false)
    const [company, setCompany] = useState(profile.company ?? '')
    const [website, setWebsite] = useState(profile.website ?? '')

    const mutation = useMutation({
        mutationFn: () => trainerProfileApi.update({ company, website }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: TRAINER_PROFILE_QUERY_KEY })
            setEditing(false)
            toast.success('Business info updated')
        },
        onError: (error) => toastApiError(error, 'Failed to update profile'),
    })

    const handleCancel = () => {
        setCompany(profile.company ?? '')
        setWebsite(profile.website ?? '')
        setEditing(false)
    }

    const logoMutation = useMutation({
        mutationFn: (file: File) => trainerProfileApi.updateLogo(file),
        onSuccess: () => {
            // Re-fetch user so profile.logo updates in the auth store
            // and the nav sidebar reflects the new logo immediately
            authApi.getUser().then((u) => {
                setUser(u)
                queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
                queryClient.invalidateQueries({ queryKey: TRAINER_PROFILE_QUERY_KEY })
            })
            toast.success('Logo updated')
        },
        onError: (error) => toastApiError(error, 'Failed to upload logo'),
    })

    if (editing) {
        return (
            <div className="py-3 flex flex-col gap-3">
                <div>
                    <Label htmlFor="company" className="text-xs text-grey-500 mb-1.5 block">
                        Company
                    </Label>
                    <Input
                        id="company"
                        value={company}
                        onChange={(e) => setCompany(e.target.value)}
                        placeholder="Your gym or business name"
                        className="h-8 text-sm"
                        autoFocus
                    />
                </div>
                <div>
                    <Label htmlFor="website" className="text-xs text-grey-500 mb-1.5 block">
                        Website
                    </Label>
                    <Input
                        id="website"
                        value={website}
                        onChange={(e) => setWebsite(e.target.value)}
                        placeholder="https://yoursite.com"
                        className="h-8 text-sm"
                    />
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
                    Business
                </p>
                <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setEditing(true)}
                    className="text-grey-600 hover:text-grey-300"
                    aria-label="Edit business info"
                >
                    <Edit2 size={13} />
                </Button>
            </div>
            <Separator className="bg-grey-800 my-2" />
            <div className="flex flex-col gap-3 py-1">
                <div className="flex items-center gap-3">
                    <LogoUpload
                        src={profile.logo || null}
                        onFileSelected={(file) => logoMutation.mutate(file)}
                        isUploading={logoMutation.isPending}
                        className="shrink-0"
                    />
                    <div>
                        <p className="text-sm text-grey-300">
                            {profile.company || (
                                <span className="text-grey-600">No company set</span>
                            )}
                        </p>
                        <p className="text-xs text-grey-600 mt-0.5">Click logo to upload</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Globe size={14} className="text-grey-500 shrink-0" />
                    {profile.website ? (
                        <a
                            href={profile.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-brand-400 hover:underline truncate"
                        >
                            {profile.website}
                        </a>
                    ) : (
                        <span className="text-sm text-grey-600">No website set</span>
                    )}
                </div>
            </div>
        </div>
    )
}

// ─── Editable Specialisms ─────────────────────────────────────────────────────

function EditableSpecialisms({ profile }: { profile: TrainerProfileType }) {
    const queryClient = useQueryClient()
    const [editing, setEditing] = useState(false)
    const [selectedGoalIds, setSelectedGoalIds] = useState<string[]>(
        profile.accepted_goals.map((g) => g.id),
    )
    const [selectedLevelIds, setSelectedLevelIds] = useState<string[]>(
        profile.accepted_levels.map((l) => l.id),
    )

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
            trainerProfileApi.update({
                accepted_goal_ids: selectedGoalIds,
                accepted_level_ids: selectedLevelIds,
            }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: TRAINER_PROFILE_QUERY_KEY })
            setEditing(false)
            toast.success('Specialisms updated')
        },
        onError: (error) => toastApiError(error, 'Failed to update specialisms'),
    })

    const handleCancel = () => {
        setSelectedGoalIds(profile.accepted_goals.map((g) => g.id))
        setSelectedLevelIds(profile.accepted_levels.map((l) => l.id))
        setEditing(false)
    }

    const toggleId = (id: string, list: string[], setList: (v: string[]) => void) => {
        setList(list.includes(id) ? list.filter((x) => x !== id) : [...list, id])
    }

    if (editing) {
        return (
            <div className="py-3 flex flex-col gap-4">
                <div>
                    <p className="text-xs text-grey-500 mb-2">Training Goals</p>
                    <div className="flex flex-wrap gap-2">
                        {goals.map((g) => {
                            const active = selectedGoalIds.includes(g.id)
                            return (
                                <button
                                    key={g.id}
                                    type="button"
                                    onClick={() =>
                                        toggleId(g.id, selectedGoalIds, setSelectedGoalIds)
                                    }
                                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                                        active
                                            ? 'bg-brand-500/20 text-brand-300 border-brand-500/40'
                                            : 'bg-grey-800 text-grey-500 border-grey-700 hover:border-grey-600'
                                    }`}
                                >
                                    {g.label}
                                </button>
                            )
                        })}
                    </div>
                </div>
                <div>
                    <p className="text-xs text-grey-500 mb-2">Experience Levels</p>
                    <div className="flex flex-wrap gap-2">
                        {levels.map((l) => {
                            const active = selectedLevelIds.includes(l.id)
                            return (
                                <button
                                    key={l.id}
                                    type="button"
                                    onClick={() =>
                                        toggleId(l.id, selectedLevelIds, setSelectedLevelIds)
                                    }
                                    className={`px-3 py-1 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                                        active
                                            ? 'bg-grey-600/40 text-grey-200 border-grey-500/40'
                                            : 'bg-grey-800 text-grey-500 border-grey-700 hover:border-grey-600'
                                    }`}
                                >
                                    {l.label}
                                </button>
                            )
                        })}
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
                    Specialisms
                </p>
                <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setEditing(true)}
                    className="text-grey-600 hover:text-grey-300"
                    aria-label="Edit specialisms"
                >
                    <Edit2 size={13} />
                </Button>
            </div>
            <Separator className="bg-grey-800 my-2" />
            <div className="flex flex-col gap-3 py-1">
                <div>
                    <p className="text-xs text-grey-500 mb-1.5">Training Goals</p>
                    {profile.accepted_goals.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                            {profile.accepted_goals.map((g) => (
                                <Badge
                                    key={g.id}
                                    className="bg-brand-500/10 text-brand-400 border-transparent"
                                >
                                    {g.label}
                                </Badge>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-grey-600">
                            No goals set — clients won't be able to find you
                        </p>
                    )}
                </div>
                <div>
                    <p className="text-xs text-grey-500 mb-1.5">Experience Levels</p>
                    {profile.accepted_levels.length > 0 ? (
                        <div className="flex flex-wrap gap-1.5">
                            {profile.accepted_levels.map((l) => (
                                <Badge
                                    key={l.id}
                                    className="bg-grey-700/40 text-grey-400 border-transparent"
                                >
                                    {l.label}
                                </Badge>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-grey-600">
                            No levels set — clients won't be able to find you
                        </p>
                    )}
                </div>
            </div>
        </div>
    )
}

// ─── Trainer Profile ──────────────────────────────────────────────────────────

export function TrainerProfile() {
    const { user } = useAuth()
    const { data: profile, isLoading } = useQuery(trainerProfileQueryOptions())

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-96">
                <div className="size-5 animate-spin rounded-full border-2 border-grey-700 border-t-brand-500" />
            </div>
        )
    }

    if (!profile) return null

    return (
        <div className="p-8 max-w-2xl">
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
                        <p className="text-sm font-medium text-grey-100 mt-0.5">{user?.email}</p>
                    </div>
                </div>
                <Separator className="bg-grey-800" />
                <div className="flex items-center gap-4 py-3">
                    <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-grey-800 text-grey-500 shrink-0">
                        <User size={15} />
                    </div>
                    <div>
                        <p className="text-xs text-grey-500">Account type</p>
                        <p className="text-sm font-medium text-grey-100 mt-0.5">Trainer</p>
                    </div>
                </div>
            </div>

            {/* Business Info */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 mb-4">
                <EditableBusinessInfo profile={profile} />
            </div>

            {/* Specialisms */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl px-4 mb-4">
                <EditableSpecialisms profile={profile} />
            </div>

            {!profile.accepted_goals.length || !profile.accepted_levels.length ? (
                <p className="text-xs text-warning-400 bg-warning-500/10 border border-warning-500/20 rounded-lg px-4 py-3">
                    Complete your specialisms so clients can find and request you.
                </p>
            ) : null}
        </div>
    )
}
