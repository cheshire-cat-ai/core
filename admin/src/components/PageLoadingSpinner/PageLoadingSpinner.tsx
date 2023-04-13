import React, { type FC } from 'react'
import clsx from 'clsx'
import Spinner from '@components/Spinner'
import { type CommonProps } from '@models/commons'

import style from './PageLoadingSpinner.module.scss'

/**
 * PageLoadingSpinner component description
 */
const PageLoadingSpinner: FC<CommonProps> = ({ className, ...rest }) => {
  const classList = clsx(style.sLoading, className)

  return (
    <div className={classList} {...rest}>
      <Spinner />
    </div>
  )
}

export default PageLoadingSpinner
