import { type JSONSchemaBasedSettings, type SettingMetadata } from '@models/JSONSchemaBasedSettings'

/**
 * TODO: Write a better documentation here.
 */
export interface EmbedderMetadata extends SettingMetadata {
  languageEmbedderName: string
  languageModelName: never
}

/**
 * TODO: DUDEEE write some documentation for fuck sake!!! embarrassing!!!
 */
export type EmbedderDescriptor = JSONSchemaBasedSettings<EmbedderMetadata>
