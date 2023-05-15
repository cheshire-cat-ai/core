import type { JSONSchema7 } from 'json-schema'

/**
 * Map the JSONSchema7 to our own type so that we can easily bump to a more 
 * recent version at some future date and only have to update this one type.
 */
export type JSONSchema = JSONSchema7

/**
 * The structure of the metadata inside each schema
 */
export interface SettingMetadata extends JSONSchema {
  readonly title: string
  readonly description: string
  readonly name_human_readable: string
}

/**
 * Map the individual settings record for each provider
 */
export type JSONSettings<TSettings = unknown> = Record<string, TSettings>

/**
 * The structure of the JSON that arrives when retriving the language models/embedders settings
 */
export interface SettingsDescriptor {
  readonly status: string
  readonly allowed_configurations: string[]
  readonly schemas: Record<string, SettingMetadata>
  readonly selected_configuration: null | string
  readonly settings: Array<{ name: string, value: JSONSettings }>
}

/**
 * The structure of the generic JSON that arrives when adding new values
 */
export interface JSONResponse {
  readonly status: 'error' | 'success'
  readonly message: string
}