import { type LLMProviderDescriptor, type LLMProviderMetaData } from '@models/LLMProviderDescriptor'
import { type UpdatableState } from '@models/commons'
import { type LLMSettings } from '@models/LLMSettings'

/**
 * Defines the structure of the redux 'llmProviders' state.
 * This state contains information about the available language models.
 */
export interface LLMProvidersState extends UpdatableState<LLMProviderDescriptor> {
  selected?: LLMProviderMetaData['languageModelName']
  settings: Record<string, LLMSettings>
}
