import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type MessagesState } from '@store/messages/types'
import { type Message } from '@models/Message'
import { uniqueId } from '@utils/commons'

const initialState: MessagesState = {
  loading: false,
  messages: [],
  defaultMessages: [
    { id: uniqueId(), sender: 'user', text: 'What\'s up?' },
    { id: uniqueId(), sender: 'user', text: 'Who\'s the Queen of Hearts?' },
    { id: uniqueId(), sender: 'user', text: 'Where is the white rabbit?' },
    { id: uniqueId(), sender: 'user', text: 'What is Python?' },
    { id: uniqueId(), sender: 'user', text: 'How do I write my own AI app?' },
    { id: uniqueId(), sender: 'user', text: 'Does pineapple belong on pizza?' }
  ]
}

/**
 *
 */
const messagesSlice = createSlice({
  name: 'messages',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload)
    }
  }
})

export const { addMessage } = messagesSlice.actions

export default messagesSlice.reducer
