/**
 * This module defines and exports a service that is used to send and receive messages to and from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */

import LogService from '@services/LogService'
import config from '@/config'

/**
 * A map of error codes to error messages.
 */
enum ErrorCodes {
  IndexError = 'Something went wrong while processing your message. Please try again later',
  SocketClosed = 'The connection to the server was closed. Please try refreshing the page',
  WebSocketConnectionError = 'Something went wrong while connecting to the server. Please try again later',
  APIError = 'Something went wrong while sending your message. Please try refreshing the page',
  FailedRetries = 'Failed to connect WebSocket after 3 retries'
}

/**
 * The WebSocket instance
 */
let socket: ReturnType<typeof useWebSocket>

/**
 * The error handler function that will be called when an error occurs
 */
let errorHandler: OnErrorHandler

/**
 * The message handler function that will be called when a message is received
 */
let messageHandler: OnMessageHandler

/**
 * MessagesService is a singleton-like object that provides a quick and easy interface for sending and receiving
 * messages from the WebSocket.
 * It wraps the WebSocket API and exposes a simple interface for sending and receiving messages.
 */
const MessagesService = Object.freeze({
  /**
   * Initializes the WebSocket connection as well as the message and error handlers
   */
  connect(onConnected: OnConnected | null = null) {
    socket = useWebSocket(config.endpoints.chat, {
      immediate: true,
      autoClose: false,
      autoReconnect: {
        retries: 3,
        delay: config.socketTimeout,
        onFailed() {
          LogService.print(ErrorCodes.FailedRetries)
        }
      },
      /*heartbeat: {
        message: JSON.stringify({ text: "ping" }),
        pongTimeout: 1000,
        interval: 1000
      },*/
      onConnected() {
        LogService.print('Connected to the WebSocket server')
        if (onConnected) {
          onConnected()
        }
      },
      onMessage(_ws, event: MessageEvent<string>) {
        if (messageHandler) {
          const data = JSON.parse(event.data) as APIMessageServiceError | APIMessageServiceResponse
          LogService.print('Received a message from the WebSocket server', data)
    
          if (isAPIMessageServiceResponse(data)) {
            messageHandler(data.content, data.why)
            return
          }
    
          if (errorHandler) {
            const errorCode = data.code as keyof typeof ErrorCodes
            const errorMessage = ErrorCodes[errorCode] || ErrorCodes.APIError
            LogService.print(errorMessage)
            errorHandler(new Error(errorMessage))
          }
        }
      },
      onError(_ws, event) {
        LogService.print('An error occurred on the WebSocket instance', event)
        if (errorHandler) {
          errorHandler(new Error(ErrorCodes.WebSocketConnectionError))
        }
      }
    })

    return this
  },
  /**
   * Sets the message handler function
   */
  onMessage(handler: OnMessageHandler) {
    messageHandler = handler
    return this
  },
  /**
   * Sets the error handler function
   */
  onError(handler: OnErrorHandler) {
    errorHandler = handler
    return this
  },
  /**
   * Send a message to the WebSocket server
   * @param message
   */
  send(message: string) {
    if (socket.status.value !== 'OPEN') {
      errorHandler(new Error(ErrorCodes.SocketClosed))
      return this
    }
    const jsonMessage = JSON.stringify({ text: message })
    socket.send(jsonMessage)
    return this
  },
  /**
   *  Close the WebSocket connection
   */
  disconnect() {
    socket.close()
  },
})

/**
 * Defines the type for the onConnected event handler.
 */
type OnConnected = () => void

/**
 * Defines the type for the onMessage event handler
 */
type OnMessageHandler = (message: string, why: any) => void

/**
 * Defines the type for the onError event handler
 */
type OnErrorHandler = (err: Error) => void

/**
 * APIMessageServiceResponse is the interface for the response from the API message service.
 */
export interface APIMessageServiceResponse {
  error: false
  content: string
  why: any
}

/**
 *  APIMessageServiceError is the interface for the error response from the API message service.
 */
export interface APIMessageServiceError {
  error: true
  code: string
}

/**
 * A type guard that takes a value of unknown type and returns a boolean indicating whether the value is of
 * type APIMessageServiceResponse
 * @param value
 */
export const isAPIMessageServiceResponse = (value: unknown): value is APIMessageServiceResponse => {
  return !!(value && typeof value === 'object' && 'content' in value && 'why' in value && 'error' in value && value.error === false)
}

export default MessagesService
