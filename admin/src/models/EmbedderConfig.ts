import type { SettingsDescriptor, SettingMetadata } from '@models/JSONSchema'

/**
 * An interface that represents an embedder schema
 */
export interface EmbedderConfigMetaData extends Omit<SettingMetadata, 'properties'> {
  readonly properties?: {
    [key: string]: {
      title?: string,
      default?: string,
      env_names?: string[],
      type?: string,
    }
  }
  readonly languageEmbedderName: string
}

/**
 * An interface that represents an embedder descriptor
 */
export interface EmbedderConfigDescriptor extends Omit<SettingsDescriptor, 'schemas'> {
  readonly schemas: Record<string, EmbedderConfigMetaData>
}