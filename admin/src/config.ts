import { AppFeatures } from '@models/AppFeatures'

const CORE_HOST = import.meta.env.CORE_HOST || 'localhost'
const CORE_PORT = import.meta.env.CORE_PORT || '1865'
const CORE_USE_SECURE_PROTOCOLS = import.meta.env.CORE_USE_SECURE_PROTOCOLS || false
const useProtocol = CORE_USE_SECURE_PROTOCOLS ? 's' : ''

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
    AppFeatures.Plugins,
    AppFeatures.WebsiteScraping
  ],
  endpoints: {
    chat: `ws${useProtocol}://${CORE_HOST}:${CORE_PORT}/ws`,
    rabbitHole: `http${useProtocol}://${CORE_HOST}:${CORE_PORT}/rabbithole/`,
    allLLM: `http${useProtocol}://${CORE_HOST}:${CORE_PORT}/settings/llm/`,
    allEmbedders: `http${useProtocol}://${CORE_HOST}:${CORE_PORT}/settings/embedder/`,
    plugins: `http${useProtocol}://${CORE_HOST}:${CORE_PORT}/plugins/`,
    wipeCollections: `http${useProtocol}://${CORE_HOST}:${CORE_PORT}/memory/wipe_collections/`
  }
}

export interface Config {
  readonly mode: string
  readonly socketTimeout: number
  readonly features: AppFeatures[]
  readonly endpoints: {
    readonly chat: string
    readonly rabbitHole: string
    readonly allLLM: string
    readonly allEmbedders: string
    readonly plugins: string
    readonly wipeCollections: string
  }
}

export default config
