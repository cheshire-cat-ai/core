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

/**
 * Safely gets the error message from a generic error map
 */
export const getErrorMessageFromErrorCodeMap = <TErrorMap extends Record<string, string>>(map: TErrorMap, key: string, defaultErr = 'Something went wrong') => {
  return map[key] || defaultErr
}
