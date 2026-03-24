import { ArrowLeft, Dumbbell, BarChart2, Users } from 'lucide-react'

const PILLARS = [
    {
        icon: Dumbbell,
        title: 'Structured Training',
        description:
            'Programs built around progressive overload with defined phases — Accumulation, Intensification, and Realisation — so every session has a purpose.',
    },
    {
        icon: BarChart2,
        title: 'Data-Driven Progress',
        description:
            "Estimated 1RM and session load tracked across time. See what's working, adjust what isn't, and build on real numbers rather than intuition.",
    },
    {
        icon: Users,
        title: 'Trainer–Client Connection',
        description:
            'Trainers and clients matched by goal and experience level. Programs, workouts, and analytics shared in one place — no more spreadsheets or chat threads.',
    },
]

export function AboutPage() {
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

            {/* Header */}
            <div className="mb-12">
                <div className="flex items-center gap-2 mb-4">
                    <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-brand-500/10">
                        <span className="text-brand-400 text-xs font-bold tracking-tight">A</span>
                    </div>
                    <span className="text-sm font-semibold text-grey-300">Apex</span>
                </div>
                <h1 className="text-3xl font-semibold text-grey-50 mb-4">
                    Personal training, built for progress
                </h1>
                <p className="text-base text-grey-400 leading-relaxed max-w-xl">
                    Apex is a full-stack personal training platform designed to bring structure,
                    accountability, and analytics to the trainer–client relationship.
                </p>
            </div>

            {/* Pillars */}
            <div className="flex flex-col gap-6 mb-12">
                {PILLARS.map(({ icon: Icon, title, description }) => (
                    <div
                        key={title}
                        className="flex gap-4 bg-grey-900 border border-grey-800 rounded-xl p-5"
                    >
                        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500/10 text-brand-400 shrink-0">
                            <Icon size={16} />
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-grey-100 mb-1">{title}</p>
                            <p className="text-xs text-grey-500 leading-relaxed">{description}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Origin */}
            <div className="bg-grey-900 border border-grey-800 rounded-xl p-6">
                <h2 className="text-sm font-semibold text-grey-200 mb-3">Why we built this</h2>
                <p className="text-xs text-grey-500 leading-relaxed mb-3">
                    Apex was built as a final year capstone project for a Full Stack Development
                    diploma. The goal was to design and ship a real, production-grade application —
                    not a toy demo — that solves a genuine problem in the fitness space.
                </p>
                <p className="text-xs text-grey-500 leading-relaxed">
                    The result is a platform that covers the full lifecycle: trainer registration
                    and specialisms, client matching, program building, workout execution, and
                    post-session analytics. Built with Django, Django REST Framework, React 19, and
                    TanStack Router.
                </p>
            </div>
        </div>
    )
}
