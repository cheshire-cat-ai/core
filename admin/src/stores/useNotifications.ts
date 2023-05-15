import type { Notification } from '@models/Notification'
import type { NotificationsState } from '@stores/types'

export const useNotifications = defineStore('notifications', () => {
  const currentState = reactive<NotificationsState>({
    history: []
  })

  const getNotifications = () => {
    return currentState.history.filter(notification => !notification.hidden)
  }

  const sendNotification = (notification: Notification) => {
    currentState.history.push(notification)
  }

  const hideNotification = (id: Notification['id']) => {
    const notificationIndex = currentState.history.findIndex(notification => notification.id === id)
    if (notificationIndex >= 0 && notificationIndex < currentState.history.length) {
      currentState.history[notificationIndex].hidden = true
    }
  }

  const showNotification = (notification: Notification, timeout = 3000) => {
    sendNotification(notification)
    const to = setTimeout(() => {
      hideNotification(notification.id)
      clearTimeout(to)
    }, timeout)
  }

  return {
    currentState,
    sendNotification,
    hideNotification,
    getNotifications,
    showNotification
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useNotifications, import.meta.hot))
}