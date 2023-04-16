/**
 * This module defines and exports a service that is used to retrieve the list of plugins from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { type Plugins } from '@models/Plugins'
import config from '../config'
import { toJSON } from '@utils/commons'

/*
 * This is a service that is used to send files down to the rabbit hole.
 * Meaning this service sends files to the backend.
 */
const PluginModels = Object.freeze({
  getPlugins: async () => {
    const endpoint = config.endpoints.plugins

    return await fetch(endpoint).then<Plugins>(toJSON)
  }
})

export default PluginModels
