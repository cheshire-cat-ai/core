/**
 * This module defines and export a collection of Typescript type guards commonly used throughout the
 * application.
 */

/**
 * A type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type string
 * @param value
 */
export const isString = (value: unknown): value is string => !!(value && typeof value === 'string')

/**
 * A type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type Error
 * @param value
 */
export const isError = (value: unknown): value is Error => value instanceof Error

/**
 * A type guard that takes a value of unknown type and returns a boolean indicating whether the value has an
 * error-like message property of type string.
 * @param value
 */
export const isErrorLikeObject = (value: unknown): value is { message: string } => {
  return !!(value && typeof value === 'object' && 'message' in value)
}
