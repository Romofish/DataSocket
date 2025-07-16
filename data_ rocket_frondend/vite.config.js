import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '127.0.0.1', // 强制绑定 IPv4，而不是默认的 ::1（IPv6 localhost）
    port: 5173
  },

})

console.log('Vite config loaded. Host:', '127.0.0.1');
// This line is for debugging purposes to confirm the config is loaded correctly
