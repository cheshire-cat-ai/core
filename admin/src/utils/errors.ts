/**
 * This module defines and export a collection of functions that are related to error management or error manipulation
 * commonly used throughout the application.
 */
import { isRouteErrorResponse } from 'react-router-dom'
import { isError, isErrorLikeObject, isString } from '@utils/typeGuards'

/**
 * Returns the error message from an error or error-like object.
 * If the value is not an error or error-like object, the unknownError argument is returned.
 */
export const getErrorMessage = (error: unknown, unknownError = 'Unknown error'): string => {
  if (isString(error)) return error
  if (isError(error) || isErrorLikeObject(error)) return error.message
  if (isRouteErrorResponse(error)) return getErrorMessage(error.error)

  return unknownError
}

/**
 * Returns the error code from an error or error-like object.
 * If the value is not an error or error-like object 'null' is returned.
 */
export const getErrorCode = (error: unknown) => {
  if (!error || typeof error !== 'object') return false
  if (isRouteErrorResponse(error)) return error.status

  const code = (error as { code?: unknown })?.code
  if (code && typeof code === 'number') return code

  const status = (error as { status?: unknown })?.status
  if (status && typeof status === 'number') return status

  return false
}
