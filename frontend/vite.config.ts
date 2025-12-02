import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // Temporarily disabled WebSocket proxy to prevent EPIPE errors
      // when backend WebSocket server is not running
      // '/ws': {
      //   target: 'ws://localhost:8000',
      //   ws: true,
      //   changeOrigin: true,
      // },
    },
  },
})
