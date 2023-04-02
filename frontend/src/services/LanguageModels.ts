/**
 * This module defines and exports a service that is used to retrieve the list of language models from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import { type LLMProviderDescriptor } from '@models/LLMProviderDescriptor'

const LanguageModels = Object.freeze({
  getProviders: async () => {
    // const endpoint = config.endpoints.settings
    // return await fetch(endpoint).then<{ settings: LanguageModel[] }>(toJSON).then(({ settings }) => settings)

    return await Promise.resolve<LLMProviderDescriptor[]>([
      { id: 1, name: 'OpenAI', description: 'OpenAI lorem ipsum dolor sit amet' },
      { id: 2, name: 'Hugging Face', description: 'Hugging Face lorem ipsum dolor sit amet' }
    ])
  }
})

export default LanguageModels
