import { type JSONSchema } from '@models/JSONSchema'
import { type LLMSettings } from '@models/LLMSettings'

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
export interface LLMProviderMetaData extends JSONSchema {
  readonly title: string
  readonly description: string
  readonly name_human_readable: string
  readonly languageModelName: string
}
