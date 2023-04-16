import { type UpdatableState } from '@models/commons'
import { type LanguageModelDescriptor, type LanguageModelMetadata } from '@models/LanguageModelDescriptor'
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'

/**
 * Defines the structure of the redux 'languageModels' state.
 * This state contains information about the available language models.
 */
export interface LanguageModelsState extends UpdatableState<LanguageModelDescriptor> {
  selected?: LanguageModelMetadata['languageModelName']
  settings: Record<string, SettingsRecord>
}
