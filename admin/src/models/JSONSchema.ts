import type { JSONSchema7 } from 'json-schema'

/**
 * Map the JSONSchema7 to our own type so that we can easily bump to a more recent version at some future date and only
 * have to update this one type.
 */
export type JSONSchema = JSONSchema7

/**
 * TODO: document this
 */
export interface SettingMetadata extends JSONSchema {
    readonly title: string
    readonly description: string
    readonly name_human_readable: string
}

/**
 * TODO: document this
 */
export type JSONSettings<TSettings = unknown> = Record<string, TSettings>

/**
 * TODO: document this
 */
export interface SettingsDescriptor {
    readonly allowed_configurations: string[]
    readonly schemas: Record<string, SettingMetadata>
    readonly selected_configuration: null | string
    readonly settings: Array<{ name: string, value: JSONSettings }>
}