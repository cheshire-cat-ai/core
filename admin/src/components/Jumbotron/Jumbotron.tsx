import React, { type FC, type PropsWithChildren } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'

import style from './Jumbotron.module.scss'

/**
 * TODO: document this
 */
const Jumbotron: FC<JumbotronProps> = ({ title, children, className, ...rest }) => {
  const classList = clsx(style.jumbo, className)

  return (
    <article className={classList} {...rest}>
      {title && <h1 className={style.title}>{title}</h1>}
      {children}
    </article>
  )
}

export interface JumbotronProps extends PropsWithChildren<CommonProps> {
  title?: string
}

export default Jumbotron
