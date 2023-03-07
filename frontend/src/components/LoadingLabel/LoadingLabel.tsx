import React, { type FC } from 'react'
import { type CommonProps } from '@models/commons'
import clsx from 'clsx'

import style from './LoadingLabel.module.scss'

/**
 * A component that displays the provided message with animated dots.
 * It is generally used to indicate that the app is loading something.
 */
const LoadingLabel: FC<LoadingLabelProps> = ({ className, children, ...rest }) => {
  const classList = clsx(style.loadingLabel, className)

  return (
    <div className={classList} {...rest}>
      {children}
      <span className={style.one}>.</span>
      <span className={style.two}>.</span>
      <span className={style.three}>.</span>
    </div>
  )
}

export interface LoadingLabelProps extends CommonProps {
  children: string
}

export default React.memo(LoadingLabel)
