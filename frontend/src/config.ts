interface Config {
  mode: string
  socketEndpoint: URL
  socketTimeout: number
  endpoints: {
    rabbitHole: URL
  }
}

/**
 * Returns the application configuration.
 * It is wrapped in a function to ensure the configuration is not mutated.
 */
const getConfig = () => Object.freeze<Config>({
  mode: import.meta.env.MODE,
  socketEndpoint: new URL('ws://localhost:1865/ws'),
  socketTimeout: 10000,
  endpoints: {
    rabbitHole: new URL('http://localhost:1865/rabbithole')
  }
})

export default getConfig
