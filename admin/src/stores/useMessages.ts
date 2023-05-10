import type { MessagesState } from '@stores/types'
import type { Message } from '@models/Message'
import { useNotifications } from '@stores/useNotifications'
import MessagesService from '@services/MessagesService'
import { now, uniqueId } from '@utils/commons'
import { getErrorMessage } from '@utils/errors'

export const useMessages = defineStore('messages', () => {
  const currentState = reactive<MessagesState>({
    ready: false,
    loading: false,
    messages: [],
    defaultMessages: [
      'What\'s up?',
      'Who\'s the Queen of Hearts?',
      'Where is the white rabbit?',
      'What is Python?',
      'How do I write my own AI app?',
      'Does pineapple belong on pizza?',
      'What is the meaning of life?',
      'What is the best programming language?',
      'What is the best pizza topping?',
      'What is a language model?',
      'What is a neural network?',
      'What is a chatbot?',
      'What time is it?',
      'Is AI capable of creating art?',
      'What is the best way to learn AI?',
      'Is it worth learning AI?',
      'Who is the Cheshire Cat?',
      'Is Alice in Wonderland a true story?',
      'Who is the Mad Hatter?',
      'How do I find my way to Wonderland?',
      'Is Wonderland a real place?'
    ]
  })

  const { showNotification } = useNotifications()

  tryOnMounted(() => {
    /**
     * Subscribes to the messages service on component mount
     * and dispatches the received messages to the store.
     * It also dispatches the error to the store if an error occurs.
     */
    MessagesService.connect(() => {
      currentState.ready = true
    }).onMessage((message, why) => {
      if (why) {
        showNotification({
          id: uniqueId(),
          type: 'info',
          message: why
        })
      } else {
        addMessage({
          id: uniqueId(),
          text: message,
          sender: 'bot',
          timestamp: now(),
          why
        })
      }
    }).onError((error: Error) => {
      currentState.loading = false
      currentState.error = getErrorMessage(error)
    })
  })

  tryOnUnmounted(() => {
    /**
     * Unsubscribes to the messages service on component unmount
     */
    MessagesService.disconnect()
  })

  /**
   * Adds a message to the list of messages
   */
  const addMessage = (msg: Message) => {
    currentState.error = undefined
    currentState.messages.push(msg)
    currentState.loading = msg.sender === 'user'
  }

  /**
 * Selects 5 random default messages from the messages slice.
 */
  const selectRandomDefaultMessages = () => {
    const defaultMessages = currentState.defaultMessages
    const messages = [...defaultMessages]
    const shuffled = messages.sort(() => 0.5 - Math.random())
    return shuffled.slice(0, 5)
  }

  /**
   * Sends a message to the messages service and optimistically dispatches it to the store
   */
  const dispatchMessage = (message: string) => {
    MessagesService.send(message)
    addMessage({
      id: uniqueId(),
      text: message.trim(),
      timestamp: now(),
      sender: 'user'
    })
  }

  return {
    currentState,
    addMessage,
    selectRandomDefaultMessages,
    dispatchMessage
  }
})