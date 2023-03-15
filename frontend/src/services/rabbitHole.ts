/**
 * This module defines and exports a service that is used to send files to the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as sending or receiving data.
 */
import getConfig from '../config'

/**
 * This is a service that is used to send files to the rabbit hole.
 */
const RabbitHoleService = Object.freeze({
  send: async (file: File) => {
    const endpoint = getConfig().endpoints.rabbitHole
    const formData = new FormData()
    formData.append('file', file)

    return await fetch(endpoint, { method: 'POST', body: formData })
  }
})

export default RabbitHoleService
