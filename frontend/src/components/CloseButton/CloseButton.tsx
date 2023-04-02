import React, { type FC, type HTMLAttributes } from 'react'
import clsx from 'clsx'

import style from './CloseButton.module.scss'

/**
 * CloseButton component description
 */
const CloseButton: FC<CloseButtonProps> = ({ className, ...rest }) => {
  const classList = clsx(style.closeBtn, className)

  return (
    <button role="button" className={classList} {...rest}>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none"
           stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2">
        <line x1="18" x2="6" y1="6" y2="18" />
        <line x1="6" x2="18" y1="6" y2="18" />
      </svg>
    </button>
  )
}

export interface CloseButtonProps extends HTMLAttributes<HTMLButtonElement> {
  onClick?: React.MouseEventHandler<HTMLButtonElement>
}

export default CloseButton
