/**
 * This module defines and export a collection of Typescript type guards commonly used throughout the
 * application.
 */
import { type APIMessageServiceResponse } from '@services/MessagesService'

/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type string
 * @param value
 */
export const isString = (value: unknown): value is string => !!(value && typeof value === 'string')

/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type Error
 * @param value
 */
export const isError = (value: unknown): value is Error => value instanceof Error

/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value has an
 * error-like message property of type string.
 * @param value
 */
export const isErrorLikeObject = (value: unknown): value is { message: string } => {
  return !!(value && typeof value === 'object' && 'message' in value)
}

/**
 * A TypeScript type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type APIMessageServiceResponse
 * @param value
 */
export const isAPIMessageServiceResponse = (value: unknown): value is APIMessageServiceResponse => {
  return !!(value && typeof value === 'object' && 'content' in value && 'why' in value && 'error' in value && value.error === false)
}
