import { type LLMProviderDescriptor } from '@models/LLMProviderDescriptor'
import { type AsyncState } from '@models/commons'

/**
 * Defines the structure of the redux 'llmProviders' state.
 * This state contains information about the available language models.
 */
export interface LLMProvidersState extends AsyncState<LLMProviderDescriptor[]> {
  selected?: LLMProviderDescriptor['id']
}
