import { join } from 'path'
import tsconfigPaths from 'vite-tsconfig-paths'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'
import IconsResolver from "unplugin-icons/resolver"
import { HeadlessUiResolver } from 'unplugin-vue-components/resolvers'
import Components from "unplugin-vue-components/vite"
import Unfonts from 'unplugin-fonts/vite'
import AutoImport from 'unplugin-auto-import/vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // when not using docker, it may be necessary to specify where the .env is
  const env = loadEnv(mode, join(process.cwd(), '../'), '')

  return {
    plugins: [
      vue(),
      AutoImport({
        dts: true,
        imports: [
          'vue',
          'vue-router',
          '@vueuse/core',
          'pinia'
        ],
        eslintrc: {
          enabled: true
        }
      }),
      Components({
        dts: true,
        resolvers: [
          HeadlessUiResolver({ prefix: "" }),
          IconsResolver({ prefix: "" })
        ]
      }),
      Icons({ autoInstall: true }),
      Unfonts({
        custom: {
          families: [{
            name: 'Ubuntu',
            local: 'Ubuntu',
            src: './src/assets/fonts/*.ttf'
          }],
          display: 'auto',
          preload: true,
          prefetch: false,
        }
      }),
      tsconfigPaths()
    ],
    define: {
      'import.meta.env.CORE_HOST': JSON.stringify(env.CORE_HOST),
      'import.meta.env.CORE_PORT': JSON.stringify(env.CORE_PORT),
      'import.meta.env.CORE_USE_SECURE_PROTOCOLS' : JSON.stringify(env.CORE_USE_SECURE_PROTOCOLS)
    },
    server: {
      port: parseInt(env.ADMIN_PORT ?? "3000"),
      open: false,
      host: true
    }
  }
})
