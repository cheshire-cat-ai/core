import getConfig from '../config'
import { type APIMessageServiceError, type APIMessageServiceResponse } from '@models/Message'
import { isAPIMessageServiceResponse } from '@utils/typeGuards'

/**
 * The WebSocket instance
 */
const { socketEndpoint } = getConfig()
const socket = new WebSocket(socketEndpoint)

/**
 *  MessagesService is a singleton that provides a simple interface for sending and receiving messages from the WebSocket server.
 *  It wraps the WebSocket API and exposes a simple interface for sending and receiving messages.
 */
export const MessagesService = Object.freeze({
  /**
   * Send a message to the WebSocket server
   * @param message
   */
  send(message: string) {
    socket.send(message)
  },

  /**
   * Open the WebSocket connection and observe the connection state.
   * It accepts two callbacks: one for when the connection is opened and one for when the connection fails.
   */
  onOpen(onOpen: (event: Event) => void, onError: (err: Error) => void) {
    socket.onerror = () => {
      onError(new Error('WebSocketConnectionError'))
    }
    socket.onopen = onOpen
  },

  /**
   * Observes the WebSocket connection for incoming messages.
   * It accepts two callbacks: one for when a message is received and one for when an error occurs.
   */
  subscribe(onSuccess: (message: string, why: any) => void, onError: (err: Error) => void) {
    socket.onmessage = (event: MessageEvent<string>) => {
      const data = JSON.parse(event.data) as APIMessageServiceError | APIMessageServiceResponse

      if (isAPIMessageServiceResponse(data)) {
        onSuccess(data.content, data.why)
        return
      }

      onError(new Error(data.code))
    }
  },

  /**
   * Unsubscribe from the WebSocket server
   */
  unsubscribe() {
    socket.onmessage = null
  },

  /**
   *  Close the WebSocket connection
   */
  close() {
    socket.close()
  }
})

/**
 * MessageServiceErrorCodes is a map of error codes to error messages.
 */
export enum MessageServiceErrorCodes {
  'WebSocketConnectionError' = 'Something went wrong while connecting to the server. Please try again later',
  'APIError' = 'Something went wrong while sending your message. Please try refreshing the page',
}

export default MessagesService
