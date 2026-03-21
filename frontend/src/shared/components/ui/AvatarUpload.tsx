import { useRef } from 'react'
import { Camera, Loader2 } from 'lucide-react'
import { Avatar, AvatarFallback, AvatarImage } from '@/shared/components/ui/avatar'
import { toast } from '@/shared/utils/toast'
import { cn } from '@/shared/utils/utils'

interface AvatarUploadProps {
    /** Current image URL — null/empty shows initials fallback */
    src?: string | null
    /** Initials to show in fallback */
    initials: string
    /** Called with the selected File — parent owns the upload mutation */
    onFileSelected: (file: File) => void
    isUploading?: boolean
    size?: 'default' | 'lg'
    className?: string
}

const MAX_SIZE_MB = 5
const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp']

export function AvatarUpload({
    src,
    initials,
    onFileSelected,
    isUploading = false,
    size = 'lg',
    className,
}: AvatarUploadProps) {
    const inputRef = useRef<HTMLInputElement>(null)

    const handleClick = () => {
        if (!isUploading) inputRef.current?.click()
    }

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0]
        if (!file) return

        if (!ACCEPTED.includes(file.type)) {
            toast.error('Unsupported format', { description: 'Please use JPEG, PNG or WebP.' })
            return
        }
        if (file.size > MAX_SIZE_MB * 1024 * 1024) {
            toast.error('File too large', { description: `Max size is ${MAX_SIZE_MB}MB.` })
            return
        }

        onFileSelected(file)
        // Reset input so the same file can be re-selected
        e.target.value = ''
    }

    return (
        <div
            className={cn('relative inline-block cursor-pointer group', className)}
            onClick={handleClick}
        >
            <Avatar
                size={size}
                className={cn('w-16 h-16 shrink-0 transition-opacity', isUploading && 'opacity-60')}
            >
                {src && <AvatarImage src={src} alt="Avatar" />}
                <AvatarFallback className="bg-brand-800 text-brand-200 text-xl font-semibold">
                    {initials}
                </AvatarFallback>
            </Avatar>

            {/* Overlay */}
            <div
                className={cn(
                    'absolute inset-0 rounded-full flex items-center justify-center transition-opacity',
                    'bg-black/50 opacity-0 group-hover:opacity-100',
                    isUploading && 'opacity-100',
                )}
            >
                {isUploading ? (
                    <Loader2 size={16} className="text-white animate-spin" />
                ) : (
                    <Camera size={14} className="text-white" />
                )}
            </div>

            <input
                ref={inputRef}
                type="file"
                accept={ACCEPTED.join(',')}
                className="hidden"
                onChange={handleChange}
            />
        </div>
    )
}
