import { AppFeatures } from '@models/AppFeatures'

const CORE_HOST = import.meta.env.CORE_HOST || 'localhost'
const CORE_PORT = import.meta.env.CORE_PORT || '1865'
const CORE_USE_SECURE_PROTOCOLS = import.meta.env.CORE_USE_SECURE_PROTOCOLS || false

const endpointsList = {
  secure : {
    chat: `wss://${CORE_HOST}:${CORE_PORT}/ws`,
    rabbitHole: `https://${CORE_HOST}:${CORE_PORT}/rabbithole/`,
    allLLM: `https://${CORE_HOST}:${CORE_PORT}/settings/llm/`,
    singleLLM: `https://${CORE_HOST}:${CORE_PORT}/settings/llm/:llm`,
    plugins: `https://${CORE_HOST}:${CORE_PORT}/plugins/`
  },
  unsecure : {
    chat: `ws://${CORE_HOST}:${CORE_PORT}/ws`,
    rabbitHole: `http://${CORE_HOST}:${CORE_PORT}/rabbithole/`,
    allLLM: `http://${CORE_HOST}:${CORE_PORT}/settings/llm/`,
    singleLLM: `http://${CORE_HOST}:${CORE_PORT}/settings/llm/:llm`,
    plugins: `http://${CORE_HOST}:${CORE_PORT}/plugins/`
  }
}

/**
 * Returns the application configuration.
 * It is wrapped in a function to ensure the configuration is not mutated.
 */
const config: Config = {
  mode: import.meta.env.MODE,
  socketTimeout: 10000,
  features: [
    AppFeatures.FileUpload,
    AppFeatures.AudioRecording,
    AppFeatures.Settings,
    AppFeatures.Plugins
  ],
  endpoints: CORE_USE_SECURE_PROTOCOLS ? endpointsList.secure : endpointsList.unsecure
}

export interface Config {
  readonly mode: string
  readonly socketTimeout: number
  readonly features: AppFeatures[]
  readonly endpoints: {
    readonly chat: string
    readonly rabbitHole: string
    readonly allLLM: string
    readonly singleLLM: string
    readonly plugins: string
  }
}

export default config
