import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/apps/krillin_ai': {
        target: 'http://127.0.0.1:8888',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/apps\/krillin_ai/, ''),
      },
      '/apps/py_video_trans': {
        target: 'http://127.0.0.1:9999',
        changeOrigin: true,
        ws: true,
        rewrite: (path) => path.replace(/^\/apps\/py_video_trans/, ''),
      },
    },
  },
})
