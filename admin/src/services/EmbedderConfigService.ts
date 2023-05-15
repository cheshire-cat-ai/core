/**
 * This module defines and exports a service that is used to retrieve the list of available embedders from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { toJSON } from '@utils/commons'
import config from '@/config'
import type { JSONSettings, JSONResponse } from '@models/JSONSchema'
import type { EmbedderConfigDescriptor } from '@models/EmbedderConfig'

/*
 * Service used to get/set the language model embedders settings.
 */
const Embedders = Object.freeze({
  getEmbedders: async () => {
    const endpoint = config.endpoints.allEmbedders

    return await fetch(endpoint).then<EmbedderConfigDescriptor>(toJSON)
  },
  setEmbedderSettings: async (languageEmbedderName: string, settings?: JSONSettings) => {
    const endpoint = config.endpoints.allEmbedders.concat(`${languageEmbedderName}`)
    try {
      await fetch(endpoint, {
        method: 'PUT',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings ?? {})
      })
      return {
        status: 'success',
        message: "Language model embedder updated successfully"
      } as JSONResponse
    } catch (error) {
      return {
        status: 'error',
        message: "Language model embedder couldn't be updated"
      } as JSONResponse
    }
  }
})

export default Embedders