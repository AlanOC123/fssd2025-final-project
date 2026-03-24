import { useNavigate } from '@tanstack/react-router'
import { ArrowLeft, ExternalLink } from 'lucide-react'
import { ROUTES } from '@/app/constants'
import { useAuth } from '@/shared/hooks/useAuth'

const AUTH_LINKS = [
    { label: 'Sign In', to: ROUTES.login },
    { label: 'Create Account', to: ROUTES.register },
    { label: 'Forgot Password', to: ROUTES.forgotPassword },
]

const TRAINER_LINKS = [
    { label: 'Dashboard', to: ROUTES.trainer.dashboard },
    { label: 'Clients', to: ROUTES.trainer.clients },
    { label: 'Programs', to: ROUTES.trainer.programs },
    { label: 'Workouts', to: ROUTES.trainer.workouts },
    { label: 'Analytics', to: ROUTES.trainer.analytics },
    { label: 'Profile', to: ROUTES.trainer.profile },
]

const CLIENT_LINKS = [
    { label: 'Dashboard', to: ROUTES.client.dashboard },
    { label: 'Workouts', to: ROUTES.client.workouts },
    { label: 'Find a Trainer', to: ROUTES.client.findTrainer },
    { label: 'Profile', to: ROUTES.client.profile },
]

const COMPANY_LINKS = [
    { label: 'About Us', to: '/about' },
    { label: 'Terms & Conditions', to: '/terms' },
    { label: 'Sitemap', to: '/sitemap' },
]

export function SitemapPage() {
    const navigate = useNavigate()
    const { user } = useAuth()

    const sections = [
        { section: 'Authentication', links: AUTH_LINKS },
        ...(user?.is_trainer ? [{ section: 'Trainer', links: TRAINER_LINKS }] : []),
        ...(user?.is_client ? [{ section: 'Client', links: CLIENT_LINKS }] : []),
        { section: 'Company', links: COMPANY_LINKS },
    ]

    return (
        <div className="min-h-dvh bg-grey-950 px-6 py-12 max-w-3xl mx-auto">
            <button
                type="button"
                onClick={() => window.history.back()}
                className="flex items-center gap-2 text-xs text-grey-500 hover:text-grey-200 transition-colors mb-10 cursor-pointer"
            >
                <ArrowLeft size={13} />
                Back
            </button>

            <div className="mb-10">
                <h1 className="text-3xl font-semibold text-grey-50 mb-3">Sitemap</h1>
                <p className="text-sm text-grey-500">All pages available on the Apex platform.</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                {sections.map(({ section, links }) => (
                    <div
                        key={section}
                        className="bg-grey-900 border border-grey-800 rounded-xl p-5"
                    >
                        <p className="text-xs font-medium text-grey-500 uppercase tracking-wider mb-4">
                            {section}
                        </p>
                        <div className="flex flex-col gap-2">
                            {links.map(({ label, to }) => (
                                <button
                                    key={to}
                                    type="button"
                                    onClick={() => navigate({ to: to as never })}
                                    className="flex items-center justify-between group text-left cursor-pointer"
                                >
                                    <span className="text-sm text-grey-400 group-hover:text-grey-100 transition-colors">
                                        {label}
                                    </span>
                                    <ExternalLink
                                        size={11}
                                        className="text-grey-700 group-hover:text-grey-500 transition-colors shrink-0"
                                    />
                                </button>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
