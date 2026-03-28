import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@/app/styles/index.css'
import { App } from '@/app/providers'

/**
 * @fileoverview Main entry point for the React application.
 * Bootstraps the application by initializing the React root and rendering
 * the provider-wrapped application component.
 */

const root = document.getElementById('root')

if (!root) {
    /**
     * Ensures the application has a valid mount point.
     * @throws {Error} If the 'root' element is missing from the index.html.
     */
    throw new Error("Root element not found. Check index.html has <div id='root'>")
}

createRoot(root).render(
    <StrictMode>
        <App />
    </StrictMode>,
)
