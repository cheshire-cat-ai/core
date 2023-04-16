/**
 * This module defines and exports a service that is used to retrieve the list of language models from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'
import { toJSON } from '@utils/commons'
import config from '../config'
import { type LanguageModelDescriptor } from '@models/LanguageModelDescriptor'

/*
 * TODO: document this
 */
const LanguageModelsService = Object.freeze({
  getProviders: async () => {
    const endpoint = config.endpoints.allLLM

    return await fetch(endpoint).then<LanguageModelDescriptor>(toJSON)
  },
  setProviderOptions: async (languageModelName: string, settings?: SettingsRecord) => {
    const endpoint = config.endpoints.singleLLM.replace(':llm', languageModelName)
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

export default LanguageModelsService
