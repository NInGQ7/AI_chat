import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    // 如果后端存在跨域问题，可以在这里配置代理，
    // 但我们的后端FastAPI通常会配置CORS，所以这里直接直连即可。
  }
})