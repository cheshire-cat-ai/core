import type { SettingsDescriptor, SettingMetadata } from '@models/JSONSchema'


/**
 * An interface that represents a language model provider schema
*/
export interface LLMProviderMetaData extends Omit<SettingMetadata, 'properties'> {
  readonly properties?: {
    [key: string]: {
      title?: string,
      default?: string,
      env_names?: string[],
      type?: string,
    }
  }
  readonly languageModelName: string
}

/**
 * An interface that represents a language model provider descriptor
 */
export interface LLMProviderDescriptor extends Omit<SettingsDescriptor, 'schemas'> {
  readonly schemas: Record<string, LLMProviderMetaData>
}