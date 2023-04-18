import { AppFeatures } from '@models/AppFeatures'
const SERVER_IP = import.meta.env.VITE_SERVER_IP
const PORT = import.meta.env.VITE_PORT
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
  endpoints: {
    chat: `ws://${SERVER_IP}:${PORT}/ws`,
    rabbitHole: `http://${SERVER_IP}:${PORT}/rabbithole`,
    allLLM: `http://${SERVER_IP}:${PORT}/settings/llm/`,
    singleLLM: `http://${SERVER_IP}:${PORT}/settings/llm/:llm`
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
    readonly singleLLM: string
  }
}

export default config
