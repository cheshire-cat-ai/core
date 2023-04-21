/**
 * This module defines and exports a service that is used to retrieve the list of plugins from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { type Plugin } from '@models/Plugin'
import config from '../config'
import { toJSON } from '@utils/commons'

/*
 * This is a service that is used to get the list of plugins active on the Cheshire Cat.
 */
const PluginsService = Object.freeze({
  getPlugins: async () => {
    const endpoint = config.endpoints.plugins

    return await fetch(endpoint).then<{ plugins: Plugin[] }>(toJSON).then(({ plugins }) => plugins)
  }
})

export default PluginsService
