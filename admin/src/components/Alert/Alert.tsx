import React, { type FC } from 'react'
import { type CommonProps } from '@models/commons'
import clsx from 'clsx'

import style from './Alert.module.scss'

/**
 * Displays an alert message.
 */
const Alert: FC<AlertProps> = ({ variant, children, className, ...rest }) => {
  const classList = clsx(style.alert, {
    [style.info]: !variant || variant === 'info',
    [style.error]: variant === 'error'
  }, className)

  return (
    <div className={classList} {...rest}>
      {children}
    </div>
  )
}

export interface AlertProps extends CommonProps {
  children: string
  /*
   * The alert variant defines the color of the alert
   */
  variant?: 'info' | 'error'
}

export default React.memo(Alert)
