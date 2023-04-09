/**
 * This module defines and exports a service that is used to retrieve the list of language models from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { type LLMProviderDescriptor } from '@models/LLMProviderDescriptor'
import { toJSON } from '@utils/commons'
import { type LLMSettings } from '@models/LLMSettings'
import getConfig from '../config'

const config = getConfig()

const LanguageModels = Object.freeze({
  getProviders: async () => {
    const endpoint = config.endpoints.languageModels

    return await fetch(endpoint).then<LLMProviderDescriptor>(toJSON)
  },
  setProviderOptions: async (languageModelName: string, settings?: LLMSettings) => {
    const llmEndpoint = config.endpoints.languageModels.href
    const endpoint = new URL(`${llmEndpoint}/${languageModelName}`)

    return await fetch(endpoint, {
      method: 'PUT',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(settings ?? {})
    })
  }
})

export default LanguageModels
