import type { JSONSchemaBasedSettings, SettingMetadata } from '@models/JSONSchemaBasedSettings'

/**
 * TODO: Write a better documentation here.
 */
export interface LanguageModelMetadata extends SettingMetadata {
  languageModelName: string
  languageEmbedderName: never
}

/**
 * A type that represents a language model provider, its settings in the form
 * of JSON schema and the current settings.
 * TODO: Write a better documentation here.
 */
export type LanguageModelDescriptor = JSONSchemaBasedSettings<LanguageModelMetadata>
