import { configureStore } from '@reduxjs/toolkit'
import messagesReducer from './messages/slice'
import fileUploaderReducer from './fileUploader/slice'
import notificationsReducer from './notifications/slice'

/**
 * The redux store
 */
const store = configureStore({
  reducer: {
    notifications: notificationsReducer,
    messages: messagesReducer,
    fileUploader: fileUploaderReducer
  }
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch

export default store
