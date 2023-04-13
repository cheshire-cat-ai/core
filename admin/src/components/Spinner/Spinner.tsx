import React, { type FC, type SVGAttributes, useMemo } from 'react'
import clsx from 'clsx'

import style from './Spinner.module.scss'

/**
 * A simple spinner component.
 */
const Spinner: FC<SpinnerProps> = ({ size, className, ...props }) => {
  const classList = clsx(style.spinner, className)
  const safeSize = size ?? 30
  const styleObj = useMemo(() => ({ width: safeSize, height: safeSize }), [safeSize])

  return (
    <div className={classList} style={styleObj}>
      <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" {...props}>
        <circle cx="50" cy="50" r="45" />
      </svg>
    </div>
  )
}

export interface SpinnerProps extends SVGAttributes<SVGElement> {
  size?: number
}

export default Spinner
