import getConfig from '../config'

/**
 * This is a service that is used to send files to the rabbit hole.
 *
 */
const RabbitHoleService = Object.freeze({
  /**
   * Sends the provided file to the rabbit hole.
   */
  send: async (file: File) => {
    const endpoint = getConfig().endpoints.rabbitHole
    const formData = new FormData()
    formData.append('file', file)

    return await fetch(endpoint, { method: 'POST', body: formData })
  }
})

export default RabbitHoleService
