import { Outlet, useNavigate, useRouterState } from '@tanstack/react-router'
import { Footer } from '@/shared/components/ui/footer'
import { Dumbbell, LayoutDashboard, LogOut, Search, UserCircle } from 'lucide-react'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'
import { useAuth } from '@/shared/hooks/useAuth'
import { toast } from '@/shared/utils/toast'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/components/ui/avatar'
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/shared/components/ui/tooltip'

interface NavItem {
    label: string
    to: string
    icon: React.ElementType
}

const NAV_ITEMS: NavItem[] = [
    { label: 'Dashboard', to: ROUTES.client.dashboard, icon: LayoutDashboard },
    { label: 'Workouts', to: ROUTES.client.workouts, icon: Dumbbell },
    { label: 'Find Trainer', to: ROUTES.client.findTrainer, icon: Search },
    { label: 'Profile', to: ROUTES.client.profile, icon: UserCircle },
]

function NavLink({ item }: { item: NavItem }) {
    const navigate = useNavigate()
    const pathname = useRouterState({ select: (s) => s.location.pathname })
    const isActive = pathname === item.to || pathname.startsWith(item.to + '/')
    const Icon = item.icon

    return (
        <button
            onClick={() => navigate({ to: item.to })}
            className={cn(
                'flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                isActive
                    ? 'bg-brand-500/15 text-brand-400'
                    : 'text-grey-500 hover:text-grey-200 hover:bg-grey-800',
            )}
            aria-current={isActive ? 'page' : undefined}
        >
            <Icon size={15} strokeWidth={isActive ? 2 : 1.75} />
            {item.label}
        </button>
    )
}

function TopNav() {
    const { logout, user } = useAuth()
    const navigate = useNavigate()

    const handleLogout = async () => {
        await logout()
        toast.success('Signed out')
        navigate({ to: ROUTES.login })
    }

    const initials =
        user?.first_name || user?.last_name
            ? `${user?.first_name?.[0] ?? ''}${user?.last_name?.[0] ?? ''}`.toUpperCase()
            : '?'

    return (
        <TooltipProvider>
            <header className="fixed top-0 left-0 right-0 h-14 flex items-center justify-between px-6 bg-grey-900 border-b border-grey-800 z-40">
                {/* Logo */}
                <div className="flex items-center gap-3">
                    <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-brand-500/10">
                        <span className="text-brand-400 text-xs font-bold tracking-tight">A</span>
                    </div>
                    <span className="text-sm font-semibold text-grey-200">Apex</span>
                </div>

                {/* Nav */}
                <nav className="flex items-center gap-1" aria-label="Client navigation">
                    {NAV_ITEMS.map((item) => (
                        <NavLink key={item.to} item={item} />
                    ))}
                </nav>

                {/* Right — avatar + logout */}
                <div className="flex items-center gap-2">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <Avatar size="sm" className="cursor-default">
                                {user?.profile &&
                                    'avatar' in user.profile &&
                                    user.profile.avatar && (
                                        <AvatarImage
                                            src={user.profile.avatar}
                                            alt={user.full_name}
                                        />
                                    )}
                                <AvatarFallback className="bg-brand-800 text-brand-200 text-xs font-semibold">
                                    {initials}
                                </AvatarFallback>
                            </Avatar>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">
                            {user?.full_name ?? user?.email}
                        </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button
                                onClick={handleLogout}
                                className="flex items-center justify-center w-8 h-8 rounded-lg text-grey-500 hover:text-danger-400 hover:bg-danger-500/10 transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                                aria-label="Sign out"
                            >
                                <LogOut size={15} strokeWidth={1.75} />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent side="bottom">Sign out</TooltipContent>
                    </Tooltip>
                </div>
            </header>
        </TooltipProvider>
    )
}

export function ClientLayout() {
    return (
        <div className="min-h-dvh bg-grey-950 flex flex-col">
            <TopNav />
            <main className="pt-14 flex-1">
                <Outlet />
            </main>
            <Footer className="ml-0" />
        </div>
    )
}
