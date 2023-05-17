/**
 * This module defines and export a collection of functions that are related to error management or error manipulation
 * commonly used throughout the application.
 */
import { isError, isErrorLikeObject, isString } from '@utils/typeGuards'

/**
 * Returns the error message from an error or error-like object.
 * If the value is not an error or error-like object, the unknownError argument is returned.
 */
export const getErrorMessage = (error: unknown, unknownError = 'Unknown error'): string => {
  if (isString(error)) return error
  if (isError(error) || isErrorLikeObject(error)) return error.message

  return unknownError
}

/**
 * Returns the error code from an error or error-like object.
 * If the value is not an error or error-like object 'null' is returned.
 */
export const getErrorCode = (error: unknown) => {
  if (!error || typeof error !== 'object') return false

  const code = (error as { code?: unknown })?.code
  if (code && typeof code === 'number') return code

  const status = (error as { status?: unknown })?.status
  if (status && typeof status === 'number') return status

  return false
}
