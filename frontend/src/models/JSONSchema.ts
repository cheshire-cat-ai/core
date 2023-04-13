import { type JSONSchema7 } from 'json-schema'

/**
 * Map the JSONSchema7 to our own type so that we can easily bump to a more recent version at some future date and only
 * have to update this one type.
 */
export type JSONSchema = JSONSchema7
