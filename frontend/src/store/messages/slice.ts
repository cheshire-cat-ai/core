import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type MessagesState } from '@store/messages/types'
import { type Message } from '@models/Message'

const initialState: MessagesState = {
  ready: false,
  loading: false,
  messages: [],
  defaultMessages: [
    'What\'s up?',
    'Who\'s the Queen of Hearts?',
    'Where is the white rabbit?',
    'What is Python?',
    'How do I write my own AI app?',
    'Does pineapple belong on pizza?'
  ]
}

/**
 * The messages slice of the redux store.
 * It contains the state of the messages sent by the user and the bot,
 * as well as a list of default messages that can be sent by the user.
 * It also contains the loading state, which tells whether the app is currently sending a message.
 *
 * Exposes the following actions:
 * - addMessage: adds a message to the list of messages
 * - toggleLoading: toggles the loading state
 */
const messagesSlice = createSlice({
  name: 'messages',
  initialState,
  reducers: {
    /**
     * Sets the ready state to true
     */
    setReady: (state) => {
      state.ready = true
    },
    /**
     * Adds a message to the list of messages
     */
    addMessage: (state, action: PayloadAction<Message>) => {
      const message = action.payload

      state.error = undefined
      state.messages.push(message)
      state.loading = message.sender === 'user'
    },
    /**
     * Sets the error state
     */
    setError: (state, action: PayloadAction<string>) => {
      state.loading = false
      state.error = action.payload
    }
  }
})

export const { addMessage, setReady, setError } = messagesSlice.actions

export default messagesSlice.reducer
