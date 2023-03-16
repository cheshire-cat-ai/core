import React, { type FC, type SVGAttributes } from 'react'
import clsx from 'clsx'

import style from './Spinner.module.scss'

/**
 * A simple spinner component.
 */
const Spinner: FC<SpinnerProps> = ({ size, className, ...props }) => {
  const classList = clsx(style.spinner, className)
  const safeSize = size ?? 25

  return (
    <svg width={safeSize} height={safeSize} className={classList} {...props} viewBox="0 0 25 25" xmlns="http://www.w3.org/2000/svg">
      <path d="M12.5238 2.07936V6.07936" />
      <path d="M12.5238 18.0794V22.0794" />
      <path d="M5.45386 5.00935L8.28386 7.83935" />
      <path d="M16.7638 16.3194L19.5938 19.1494" />
      <path d="M2.5238 12.0794H6.5238" />
      <path d="M18.5238 12.0794H22.5238" />
      <path d="M5.45386 19.1494L8.28386 16.3194" />
      <path d="M16.7638 7.83935L19.5938 5.00935" />
    </svg>
  )
}

export interface SpinnerProps extends SVGAttributes<SVGElement> {
  size: number
}

export default Spinner
