import { join } from 'path'
import tsconfigPaths from 'vite-tsconfig-paths'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // when not using docker, it may be necessary to specify where the .env is
  const env = loadEnv(mode, join(process.cwd(), '../'), '')

  return {
    plugins: [vue(), tsconfigPaths()],
    define: {
      'import.meta.env.CORE_HOST': JSON.stringify(env.CORE_HOST),
      'import.meta.env.CORE_PORT': JSON.stringify(env.CORE_PORT),
      'import.meta.env.API_KEY': JSON.stringify(env.API_KEY),
      'import.meta.env.CORE_USE_SECURE_PROTOCOLS' : JSON.stringify(env.CORE_USE_SECURE_PROTOCOLS)
    },
    server: {
      port: parseInt(env.ADMIN_PORT ?? "3000"),
      open: false,
      host: true
    }
  }
})
