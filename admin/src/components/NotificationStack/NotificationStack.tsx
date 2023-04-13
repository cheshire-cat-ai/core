import React, { type FC, type HTMLAttributes } from 'react'
import clsx from 'clsx'
import { type Notification } from '@models/Notification'

import style from './NotificationStack.module.scss'

/**
 * A stateless component used to display  a stack of notifications on the screen.
 */
const NotificationStack: FC<NotificationStackProps> = ({ notifications, className, ...rest }) => {
  const classList = clsx(style.notificationStack, notifications.length > 0 && style.hasNotifications, className)

  return (
    <div className={classList} {...rest}>
      {notifications.map((notification) => <NotificationBox entity={notification} key={notification.id} />)}
    </div>
  )
}

/**
 * A stateless component used to display a single notification on the screen.
 */
const NotificationBox: FC<{ entity: Notification }> = ({ entity }) => {
  const classList = clsx(style.notification, {
    [style.info]: !entity.type || entity.type === 'info',
    [style.error]: entity.type === 'error',
    [style.success]: entity.type === 'success'
  })

  return (
    <div role="alert" className={classList}>
      {entity.message}
    </div>
  )
}

export interface NotificationStackProps extends HTMLAttributes<HTMLElement> {
  /*
   * The notifications to be displayed
   */
  notifications: Notification[]
}

export default React.memo(NotificationStack)
