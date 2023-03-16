import { useCallback } from 'react'
import { useDispatch } from 'react-redux'
import { type Notification } from '@models/Notification'
import { hideNotification, sendNotification } from '@store/notifications/slice'

/**
 * A custom hook [...]
 */
const useNotifications = () => {
  const dispatch = useDispatch()

  const showNotification = useCallback((notification: Notification, timeout = 3000) => {
    dispatch(sendNotification({ notification }))

    const to = setTimeout(() => {
      dispatch(hideNotification({ notificationId: notification.id }))
      clearTimeout(to)
    }, timeout)
  }, [dispatch])

  return { showNotification }
}

export default useNotifications
