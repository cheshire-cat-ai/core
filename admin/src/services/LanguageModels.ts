/**
 * This module defines and exports a service that is used to retrieve the list of language models from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import type { LLMProviderDescriptor, LLMSettings } from '@models/LLMProvider'
import { toJSON } from '@utils/commons'
import config from '../config'

/*
 * This is a service that is used to send files down to the rabbit hole.
 * Meaning this service sends files to the backend.
 */
const LanguageModels = Object.freeze({
  getProviders: async () => {
    const endpoint = config.endpoints.allLLM

    return await fetch(endpoint).then<LLMProviderDescriptor>(toJSON)
  },
  setProviderOptions: async (languageModelName: string, settings?: LLMSettings) => {
    const endpoint = config.endpoints.singleLLM.replace(':llm', languageModelName)
    try {
      return await fetch(endpoint, {
        method: 'PUT',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(settings ?? {})
      })
    } catch (error) {
      return new Error("Language model provider couldn't be updated")
    }
  }
})

export default LanguageModels
