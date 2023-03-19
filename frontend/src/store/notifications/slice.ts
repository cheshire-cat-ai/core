import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type NotificationsState } from '@store/notifications/types'
import { type Notification } from '@models/Notification'

const initialState: NotificationsState = {
  history: []
}

/**
 * The 'notifications' slice of the redux store.
 * It contains the state of the notifications that the user has received.
 */
const notificationsSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    sendNotification: (state, action: PayloadAction<{ notification: Notification }>) => {
      state.history.push(action.payload.notification)
    },
    hideNotification: (state, action: PayloadAction<{ notificationId: Notification['id'] }>) => {
      const { notificationId } = action.payload
      const notificationIndex = state.history.findIndex((notification) => notification.id === notificationId)

      state.history[notificationIndex].hidden = true
    }
  }
})

export const { sendNotification, hideNotification } = notificationsSlice.actions

export default notificationsSlice.reducer
