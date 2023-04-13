/**
 * This module defines and exports a service that is used to send files to the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import LogService from '@services/LogService'
import { toJSON } from '@utils/commons'
import config from '../config'

const endpoint = config.endpoints.rabbitHole

/*
 * This service is used to send files down to the rabbit hole.
 * Meaning this service sends files to the backend... lol
 */
const RabbitHoleService = Object.freeze({
  send: async (file: File) => {
    const formData = new FormData()
    const options = { method: 'POST', body: formData }

    formData.append('file', file)

    LogService.print('Sending a file to the rabbit hole', { endpoint, options })

    return await fetch(endpoint, options).then<RabbitHoleServiceResponse>(toJSON)
  }
})

export interface RabbitHoleServiceResponse {
  'content-type': 'text/plain' | 'text/markdown' | 'application/pdf'
  filename: string
  info: string
}

export default RabbitHoleService
