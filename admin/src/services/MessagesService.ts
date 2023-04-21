/**
 * This module defines and exports a service that is used to send and receive messages to and from the backend.
 * A service is a singleton object that provides a simple interface for performing backend-related tasks such as
 * sending or receiving data.
 */

import { isAPIMessageServiceResponse } from '@utils/typeGuards'
import LogService from '@services/LogService'
import config from '../config'

/**
 * The WebSocket instance
 */
let socket: WebSocket

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
    let isReady = false
    socket = new WebSocket(config.endpoints.chat)

    socket.onopen = (event) => {
      if (onConnected) {
        LogService.print('Connected to the WebSocket server')
        onConnected(event)
        isReady = true
      }
    }

    /**
     * Handles the incoming messages from the WebSocket server
     */
    socket.onmessage = (event: MessageEvent<string>) => {
      if (isReady && messageHandler) {
        const data = JSON.parse(event.data) as APIMessageServiceError | APIMessageServiceResponse
        LogService.print('Received a message from the WebSocket server', data)

        if (isAPIMessageServiceResponse(data)) {
          messageHandler(data.content, data.why)
          return
        }

        const errorCode = data.code as keyof typeof MessagesService.ErrorCodes
        const errorMessage = MessagesService.ErrorCodes[errorCode] || MessagesService.ErrorCodes.APIError
        errorHandler(new Error(errorMessage))
      }
    }

    /**
     *  Handles the WebSocket connection errors
     */
    socket.onerror = (event) => {
      LogService.print('An error occurred on the WebSocket instance', event)
      if (errorHandler) {
        errorHandler(new Error(MessagesService.ErrorCodes.WebSocketConnectionError))
      }
    }

    /**
     * Handles the WebSocket connection close
     */
    const tm = setTimeout(() => {
      if (socket.readyState === WebSocket.CONNECTING) {
        LogService.print(`The socket has been forcefully closed due to a timeout of ${config.socketTimeout}ms`)
        errorHandler(new Error(MessagesService.ErrorCodes.WebSocketConnectionError))
        MessagesService.disconnect()
        clearTimeout(tm)
      }
    }, config.socketTimeout)

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
    if (socket.readyState !== WebSocket.OPEN) {
      errorHandler(new Error(MessagesService.ErrorCodes.SocketClosed))
      return this
    }

    const jsonMessage = JSON.stringify({
      text: message
    })
    socket.send(jsonMessage)

    return this
  },
  /**
   * Unsubscribe from the WebSocket server
   */
  unsubscribe() {
    socket.onopen = null
    socket.onmessage = null
    socket.onmessage = null

    return this
  },
  /**
   *  Close the WebSocket connection
   */
  disconnect() {
    socket.close()
    return MessagesService.unsubscribe()
  },
  /**
   * a map of error codes to error messages.
   */
  ErrorCodes: Object.freeze({
    IndexError: 'Something went wrong while processing your message. Please try again later',
    SocketClosed: 'The connection to the server was closed. Please try refreshing the page',
    WebSocketConnectionError: 'Something went wrong while connecting to the server. Please try again later',
    APIError: 'Something went wrong while sending your message. Please try refreshing the page'
  })
})

/**
 * Defines the type for the onConnected event handler.
 */
type OnConnected = (event: Event) => void

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

export default MessagesService
