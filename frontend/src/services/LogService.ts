/**
 * This module defines and exports a service that is used to console.log messages for debugging purposes.
 * It doesn't do anything in production mode.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */
import config from '../config'

/**
 * This is a service that is used to log messages to the console in development mode.
 */
const LogService = Object.freeze({
  print: (...args: any[]) => {
    if (config.mode === 'development') {
      console.log('🐱 log:', ...args)
    }
  }
})

export default LogService
