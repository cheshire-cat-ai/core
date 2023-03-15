/**
 * This module defines and export a collection of functions that are related to error management or error manipulation
 * commonly used throughout the application.
 */
import { isError, isErrorLikeObject, isString } from '@utils/typeGuards'

/**
 * Returns the error message from an error or error-like object.
 * If the value is not an error or error-like object, the unknownError argument is returned.
 */
export const getErrorMessage = (error: unknown, unknownError = 'Unknown error') => {
  if (isString(error)) return error
  if (isError(error) || isErrorLikeObject(error)) return error.message

  return unknownError
}
