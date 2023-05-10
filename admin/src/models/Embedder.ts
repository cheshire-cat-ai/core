import type { SettingsDescriptor, SettingMetadata } from '@models/JSONSchema'

/**
 * An interface that represents an embedder schema
 */
export interface EmbedderMetaData extends Omit<SettingMetadata, 'properties'> {
    readonly properties?: {
        [key: string]: {
            title?: string,
            default?: string,
            env_names?: string[],
            type?: string,
        }
    }
    languageEmbedderName: string
    languageModelName: never
}

/**
 * An interface that represents an embedder descriptor
 */
export interface EmbedderDescriptor extends Omit<SettingsDescriptor, 'schemas'> {
    readonly schemas: Record<string, EmbedderMetaData>
}