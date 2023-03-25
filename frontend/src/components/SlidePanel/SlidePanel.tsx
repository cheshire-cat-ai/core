import React, { type FC, type PropsWithChildren } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'

import styles from './SlidePanel.module.scss'

/**
 * SlidePanel component description
 */
const SlidePanel: FC<SlideInPanelProps> = ({ active, variant, className, children, ...rest }) => {
  const classList = clsx(styles.slidePanel, active && styles.active, {
    [styles.fromLeft]: !variant || variant === 'from-left',
    [styles.fromRight]: variant === 'from-right'
  }, className)

  return (
    <aside className={classList} {...rest}>
      {children}
    </aside>
  )
}

export interface SlideInPanelProps extends PropsWithChildren<CommonProps> {
  active?: boolean
  variant?: 'from-left' | 'from-right'
}

export default SlidePanel
