import type { JSONSchema } from '@models/JSONSchema'

/**
 * A type that represents a language model provider descriptor
 */
export interface LLMProviderDescriptor {
  readonly allowed_configurations: string[]
  readonly schemas: Record<string, LLMProviderMetaData>
  readonly selected_configuration: null | string
  readonly settings: Array<{ name: string, value: LLMSettings }>
}

/**
 * A type that represents a language model provider schema
 */
export interface LLMProviderMetaData extends Omit<JSONSchema, 'properties'> {
  readonly title: string
  readonly description: string
  readonly name_human_readable: string
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

export type LLMSettings<TSettings = any> = Record<string, TSettings>
