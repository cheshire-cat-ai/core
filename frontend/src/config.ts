interface Config {
  mode: string
  socketEndpoint: string
  socketTimeout: number
}

/**
 * Returns the application configuration.
 * It is wrapped in a function to ensure the configuration is not mutated.
 */
const getConfig = () => Object.freeze<Config>({
  mode: import.meta.env.MODE,
  socketEndpoint: import.meta.env.VITE_SOCKET_ENDPOINT,
  socketTimeout: import.meta.env.VITE_SOCKET_ENDPOINT_TIMEOUT_MS || 10000
})

export default getConfig
