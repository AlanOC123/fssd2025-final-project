import { Outlet, useNavigate, useRouterState } from '@tanstack/react-router'
import { LayoutDashboard, Users, Dumbbell, BookOpen, BarChart2, LogOut } from 'lucide-react'
import { cn } from '@/shared/utils/utils'
import { ROUTES } from '@/app/constants'
import { useAuth } from '@/shared/hooks/useAuth'
import { toast } from '@/shared/utils/toast'
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
    { label: 'Dashboard', to: ROUTES.trainer.dashboard, icon: LayoutDashboard },
    { label: 'Clients', to: ROUTES.trainer.clients, icon: Users },
    { label: 'Programs', to: ROUTES.trainer.programs, icon: BookOpen },
    { label: 'Workouts', to: ROUTES.trainer.workouts, icon: Dumbbell },
    { label: 'Analytics', to: ROUTES.trainer.analytics, icon: BarChart2 },
]

function NavLink({ item }: { item: NavItem }) {
    const navigate = useNavigate()
    const pathname = useRouterState({ select: (s) => s.location.pathname })
    const isActive = pathname === item.to || pathname.startsWith(item.to + '/')
    const Icon = item.icon

    return (
        <Tooltip>
            <TooltipTrigger asChild>
                <button
                    onClick={() => navigate({ to: item.to })}
                    className={cn(
                        'relative flex items-center justify-center w-10 h-10 rounded-lg transition-all duration-200 cursor-pointer',
                        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500',
                        isActive
                            ? 'bg-brand-500/15 text-brand-400'
                            : 'text-grey-500 hover:text-grey-200 hover:bg-grey-800',
                    )}
                    aria-label={item.label}
                    aria-current={isActive ? 'page' : undefined}
                >
                    {isActive && (
                        <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-brand-500 -ml-3" />
                    )}
                    <Icon size={18} strokeWidth={isActive ? 2 : 1.75} />
                </button>
            </TooltipTrigger>
            <TooltipContent side="right" sideOffset={12}>
                {item.label}
            </TooltipContent>
        </Tooltip>
    )
}

function Sidebar() {
    const navigate = useNavigate()
    const { logout, user } = useAuth()

    const handleLogout = async () => {
        await logout()
        toast.success('Signed out')

        navigate({ to: ROUTES.login })
    }

    const initials = user
        ? `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase()
        : '?'

    return (
        <TooltipProvider>
            <aside className="fixed left-0 top-0 h-dvh w-16 flex flex-col items-center py-4 bg-grey-900 border-r border-grey-800 z-40">
                {/* Logo mark */}
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-brand-500/10 mb-6">
                    <span className="text-brand-400 text-sm font-bold tracking-tight">A</span>
                </div>

                {/* Nav */}
                <nav
                    className="flex flex-col items-center gap-1 flex-1"
                    aria-label="Trainer navigation"
                >
                    {NAV_ITEMS.map((item) => (
                        <NavLink key={item.to} item={item} />
                    ))}
                </nav>

                {/* Bottom — avatar + logout */}
                <div className="flex flex-col items-center gap-2">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-brand-800 text-brand-200 text-xs font-semibold select-none cursor-default">
                                {initials}
                            </div>
                        </TooltipTrigger>
                        <TooltipContent side="right" sideOffset={12}>
                            {user?.full_name ?? user?.email}
                        </TooltipContent>
                    </Tooltip>

                    <Tooltip>
                        <TooltipTrigger asChild>
                            <button
                                onClick={handleLogout}
                                className="flex items-center justify-center w-10 h-10 rounded-lg text-grey-500 hover:text-danger-400 hover:bg-danger-500/10 transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500"
                                aria-label="Sign out"
                            >
                                <LogOut size={18} strokeWidth={1.75} />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent side="right" sideOffset={12}>
                            Sign out
                        </TooltipContent>
                    </Tooltip>
                </div>
            </aside>
        </TooltipProvider>
    )
}

export function TrainerLayout() {
    return (
        <div className="min-h-dvh bg-grey-950 flex">
            <Sidebar />
            {/* offset content by sidebar width */}
            <main className="flex-1 ml-16 min-w-0">
                <Outlet />
            </main>
        </div>
    )
}
