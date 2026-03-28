import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import checker from 'vite-plugin-checker'
import path from 'path'

/**
 * Vite configuration for the React project.
 * * Configures build plugins for TanStack Router, React, Tailwind CSS,
 * and TypeScript type checking. Sets up path aliases and dev server proxies.
 */
export default defineConfig({
    plugins: [
        tanstackRouter({
            routesDirectory: './src/routes',
            generatedRouteTree: './src/routeTree.gen.ts',
        }),
        react(),
        tailwindcss(),
        checker({ typescript: true }),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        host: '0.0.0.0',
        port: 5173,
        proxy: {
            // Proxies API and media requests to the backend service container.
            '/api': {
                target: 'http://web:8000',
                changeOrigin: true,
            },
            '/media': {
                target: 'http://web:8000',
                changeOrigin: true,
            },
        },
    },
})
