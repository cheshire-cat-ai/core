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
}

/**
 * The 'messages' slice of the redux store.
 * It contains the state of the messages sent by the user and the bot,
 * as well as a list of default messages that can be sent by the user.
 * It also contains the loading state, which tells whether the app is currently sending a message.
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
