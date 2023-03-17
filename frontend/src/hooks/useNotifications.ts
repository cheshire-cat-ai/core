import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { type Notification } from '@models/Notification'
import { hideNotification, sendNotification } from '@store/notifications/slice'
import { selectNotifications } from '@store/notifications/selectors'

/**
 * A custom hook that returns the notifications state and a function to show a notification.
 * When displaying a notification, a timeout is set to hide it after a certain amount of time.
 */
const useNotifications = () => {
  const notifications = useSelector(selectNotifications)
  const dispatch = useDispatch()

  const showNotification = useCallback((notification: Notification, timeout = 5000) => {
    dispatch(sendNotification({ notification }))

    const to = setTimeout(() => {
      dispatch(hideNotification({ notificationId: notification.id }))
      clearTimeout(to)
    }, timeout)
  }, [dispatch])

  return { notifications, showNotification }
}

export default useNotifications
