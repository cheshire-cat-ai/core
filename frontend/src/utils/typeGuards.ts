/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value is of type string
 * @param value
 */
export const isString = (value: unknown): value is string => !!(value && typeof value === 'string')

/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value is of type number
 * @param value
 */
export const isNumber = (value: unknown): value is string => !!(value && typeof value === 'number')
