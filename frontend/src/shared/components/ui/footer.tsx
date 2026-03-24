import { useNavigate } from '@tanstack/react-router'
import { Github, Twitter, Instagram } from 'lucide-react'
import { cn } from '@/shared/utils/utils'

const FOOTER_LINKS = {
    company: [
        { label: 'About Us', to: '/about' },
        { label: 'Terms & Conditions', to: '/terms' },
    ],
    platform: [{ label: 'Sitemap', to: '/sitemap' }],
}

const SOCIAL_LINKS = [
    { label: 'GitHub', icon: Github, href: '#' },
    { label: 'Twitter', icon: Twitter, href: '#' },
    { label: 'Instagram', icon: Instagram, href: '#' },
]

interface FooterProps {
    className?: string
}

export function Footer({ className }: FooterProps) {
    const navigate = useNavigate()

    return (
        <footer className={cn('border-t border-grey-800/60 bg-grey-950 mt-auto', className)}>
            <div className="px-8 py-8">
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-8">
                    {/* Brand */}
                    <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                            <div className="flex items-center justify-center w-6 h-6 rounded-md bg-brand-500/10">
                                <span className="text-brand-400 text-xs font-bold tracking-tight">
                                    A
                                </span>
                            </div>
                            <span className="text-sm font-semibold text-grey-200">Apex</span>
                        </div>
                        <p className="text-xs text-grey-600 max-w-48 leading-relaxed">
                            Personal training, structured and data-driven.
                        </p>
                    </div>

                    {/* Links */}
                    <div className="flex gap-12">
                        <div className="flex flex-col gap-3">
                            <p className="text-xs font-medium text-grey-500 uppercase tracking-wider">
                                Company
                            </p>
                            {FOOTER_LINKS.company.map((link) => (
                                <button
                                    key={link.to}
                                    type="button"
                                    onClick={() => navigate({ to: link.to })}
                                    className="text-xs text-grey-500 hover:text-grey-200 transition-colors text-left cursor-pointer"
                                >
                                    {link.label}
                                </button>
                            ))}
                        </div>
                        <div className="flex flex-col gap-3">
                            <p className="text-xs font-medium text-grey-500 uppercase tracking-wider">
                                Platform
                            </p>
                            {FOOTER_LINKS.platform.map((link) => (
                                <button
                                    key={link.to}
                                    type="button"
                                    onClick={() => navigate({ to: link.to })}
                                    className="text-xs text-grey-500 hover:text-grey-200 transition-colors text-left cursor-pointer"
                                >
                                    {link.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Social */}
                    <div className="flex flex-col gap-3">
                        <p className="text-xs font-medium text-grey-500 uppercase tracking-wider">
                            Follow
                        </p>
                        <div className="flex items-center gap-2">
                            {SOCIAL_LINKS.map(({ label, icon: Icon, href }) => (
                                <a
                                    key={label}
                                    href={href}
                                    aria-label={label}
                                    className="flex items-center justify-center w-7 h-7 rounded-lg text-grey-600 hover:text-grey-300 hover:bg-grey-800 transition-all duration-200"
                                >
                                    <Icon size={14} />
                                </a>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Bottom bar */}
                <div className="mt-8 pt-6 border-t border-grey-800/40 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                    <p className="text-xs text-grey-700">
                        © {new Date().getFullYear()} Apex. All rights reserved.
                    </p>
                    <p className="text-xs text-grey-700">Built with Django &amp; React</p>
                </div>
            </div>
        </footer>
    )
}
