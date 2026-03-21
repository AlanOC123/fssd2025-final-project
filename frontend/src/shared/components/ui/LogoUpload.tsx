import { useRef } from 'react'
import { Camera, Loader2, Building2 } from 'lucide-react'
import { toast } from '@/shared/utils/toast'
import { cn } from '@/shared/utils/utils'

interface LogoUploadProps {
    src?: string | null
    onFileSelected: (file: File) => void
    isUploading?: boolean
    className?: string
}

const MAX_SIZE_MB = 5
const ACCEPTED = ['image/jpeg', 'image/png', 'image/webp']

export function LogoUpload({
    src,
    onFileSelected,
    isUploading = false,
    className,
}: LogoUploadProps) {
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
        e.target.value = ''
    }

    return (
        <div
            onClick={handleClick}
            className={cn(
                'relative flex items-center justify-center w-16 h-16 rounded-xl cursor-pointer group',
                'bg-grey-800 border border-grey-700 transition-colors hover:border-grey-600',
                isUploading && 'opacity-60',
                className,
            )}
        >
            {src ? (
                <img
                    src={src}
                    alt="Company logo"
                    className="w-full h-full object-contain rounded-xl"
                />
            ) : (
                <Building2 size={22} className="text-grey-500" />
            )}

            {/* Overlay */}
            <div
                className={cn(
                    'absolute inset-0 rounded-xl flex items-center justify-center transition-opacity',
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
