import { AppFeatures } from '@models/AppFeatures'

/**
 * Returns the application configuration.
 * It is wrapped in a function to ensure the configuration is not mutated.
 */
const getConfig = () => Object.freeze<Config>({
  mode: import.meta.env.MODE,
  socketTimeout: 10000,
  features: [
    AppFeatures.FileUpload,
    AppFeatures.AudioRecording,
    AppFeatures.Configurations,
    AppFeatures.Plugins
  ],
  endpoints: {
    chat: new URL('ws://localhost:1865/ws'),
    rabbitHole: new URL('http://localhost:1865/rabbithole')
  }
})

export interface Config {
  readonly mode: string
  readonly socketTimeout: number
  readonly features: AppFeatures[]
  readonly endpoints: {
    readonly chat: URL
    readonly rabbitHole: URL
  }
}

export default getConfig
