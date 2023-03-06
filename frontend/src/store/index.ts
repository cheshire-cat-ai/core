import { configureStore } from '@reduxjs/toolkit'
import messagesReducer from './messages/slice'

const store = configureStore({
  reducer: {
    messages: messagesReducer
  }
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch

export default store
