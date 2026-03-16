import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@/app/styles/index.css'
import { App } from '@/app/providers'

const root = document.getElementById('root')

if (!root) {
    throw new Error("Root element not found. Check index.html has <div id='root'>")
}

createRoot(root).render(
    <StrictMode>
        <App />
    </StrictMode>,
)
