import { type JSONSchema } from '@models/JSONSchema'

/**
 * A type that represents a language model provider descriptor
 */
export interface LLMProviderDescriptor {
  readonly settings: []
  readonly allowed_llm_configurations: string[]
  readonly schemas: Record<string, LLMProviderMetaData>
}

/**
 * A type that represents a language model provider schema
 */
export interface LLMProviderMetaData extends JSONSchema {
  title: string
  description: string
  name_human_readable: string
  languageModelName: string
}
