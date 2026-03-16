import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // Django 后端地址
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/stu_practice': {
        target: 'http://localhost:8000', // legacy stu_practice 视图（练习详情等）
        changeOrigin: true
      }
    }
  }
})
