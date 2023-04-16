import { type UpdatableState } from '@models/commons'
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'
import { type EmbedderDescriptor, type EmbedderMetadata } from '@models/EmbedderDescriptor'

/**
 * TODO: define this
 */
export interface EmbeddersState extends UpdatableState<EmbedderDescriptor> {
  selected?: EmbedderMetadata['languageEmbedderName']
  settings: Record<string, SettingsRecord>
}
