/**
 * This module defines and exports a service that is used to retrieve the list of available embedders from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { toJSON } from '@utils/commons'
import config from '@/config'
import type { EmbedderDescriptor } from '@models/Embedder'

/*
 * TODO: document this
 */
const EmbeddersService = Object.freeze({
    getEmbedders: async () => {
        const endpoint = config.endpoints.allEmbedders

        return await fetch(endpoint).then<EmbedderDescriptor>(toJSON)
    }
})

export default EmbeddersService