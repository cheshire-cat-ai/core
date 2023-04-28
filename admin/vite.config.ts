import { defineConfig, loadEnv } from 'vite'
import { resolve } from 'path'
import react from '@vitejs/plugin-react-swc'
import postCSSPresetEnv from 'postcss-preset-env'
import autoprefixer from 'autoprefixer'
import postCSSPxToRem from 'postcss-pxtorem'
import svgr from 'vite-plugin-svgr'

const rootDir = resolve(__dirname)



/**
 * The Vite configuration file.
 * @see https://vitejs.dev/config/
*/
export default defineConfig(options => {

  // when not using docker, it may be necessary to specify where the .env is
  process.env = {...process.env, ...loadEnv(options.mode, process.cwd())}

  const config = {
    define: {
      'import.meta.env.CORE_HOST': JSON.stringify(process.env.CORE_HOST),
      'import.meta.env.CORE_PORT': JSON.stringify(process.env.CORE_PORT),
      'import.meta.env.API_KEY': JSON.stringify(process.env.API_KEY),
      'import.meta.env.CORE_USE_SECURE_PROTOCOLS' : JSON.stringify(process.env.CORE_USE_SECURE_PROTOCOLS),
    },
    server: {
      port: 3000,
      open: true,
      host: true
    },
    resolve: {
      /**
       * Aliases for the project need to match the tsconfig.json ones.
       * Please make sure to update both files.
       */
      alias: {
        '@hooks': resolve(rootDir, 'src', 'hooks'),
        '@components': resolve(rootDir, 'src', 'components'),
        '@models': resolve(rootDir, 'src', 'models'),
        '@routes': resolve(rootDir, 'src', 'routes'),
        '@services': resolve(rootDir, 'src', 'services'),
        '@store': resolve(rootDir, 'src', 'store'),
        '@theme': resolve(rootDir, 'src', 'theme'),
        '@utils': resolve(rootDir, 'src', 'utils')
      }
    },
    css: {
      modules: {
        /**
         * Generates a unique class name for each component composed by the 'ccat' prefix,
         * the module name and the class name
         */
        generateScopedName: 'ccat-[name]-[local]'
      },
      preprocessorOptions: {
        /**
         * The mixins file is imported in every SCSS file.
         */
        scss: {
          additionalData: `@import "@theme/mixins";`
        }
      },
      postcss: {
        plugins: [
          autoprefixer,
          postCSSPresetEnv({ stage: 3 }),
          postCSSPxToRem({ propList: ['*'] })
        ]
      }
    },
    plugins: [
      svgr({ exportAsDefault: true }),
      react()
    ]
  }

  return config
})
