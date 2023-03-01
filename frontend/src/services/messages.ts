/**
 * The WebSocket instance
 */
const socket = new WebSocket('ws://localhost:1865/ws')

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
   * Observe the WebSocket server for messages
   * @param callback
   */
  subscribe(callback: (message: string, why: any) => void) {
    socket.onmessage = (event: MessageEvent<string>) => {
      const data = JSON.parse(event.data) as { content: string, why: any }
      callback(data.content, data.why)
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

export default MessagesService
