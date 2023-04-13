import React, { type FC } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'

import styles from './Logo.module.scss'

/**
 * Logo component description
 */
const Logo: FC<LogoProps> = ({ className, ...rest }) => {
  const classList = clsx(styles.logo, className)

  return (
    <div className={classList} {...rest}>
      😺
    </div>
  )
}

export interface LogoProps extends CommonProps {
}

export default Logo
