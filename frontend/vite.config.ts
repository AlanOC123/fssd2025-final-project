import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    watch: {
      usePolling: true
    },
    proxy: {
      '/api': {
        target: "http://web:8000",
        changeOrigin: true,
        secure: false
      },
      '/admin': {
        target: "http://web:8000",
        changeOrigin: true,
        secure: false
      },
      '/static': {
        target: "http://web:8000",
        changeOrigin: true,
        secure: false
      }
    }
  }
})
