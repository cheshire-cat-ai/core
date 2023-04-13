import React, { type ButtonHTMLAttributes, type FC } from 'react'
import clsx from 'clsx'

import style from './HamburgerButton.module.scss'

/**
 * A stateless/controlled component displaying an SVG hamburger button that can be used to
 * toggle the visibility of a navigation menu.
 *
 * By keeping this component stateless/controlled, we can more easily manage the state of a possible external
 * navigation menu and ensure that the button and menu are always in sync.
 * This is generally helpful in a complex codebase where the state of the navigation menu may be managed
 * by a separate component or module.
 */
const HamburgerButton: FC<HamburgerButtonProps> = ({ active, className, ...rest }) => {
  const classList = clsx(style.hamBtn, active && style.active, className)

  return (
    <button className={classList} {...rest}>
      <svg viewBox="0 0 100 100">
        <path className={style.top}
              d="m 30,33 h 40 c 3.722839,0 7.5,3.126468 7.5,8.578427 0,5.451959 -2.727029,8.421573 -7.5,8.421573 h -20" />
        <path className={style.middle}
              d="m 30,50 h 40" />
        <path className={style.bottom}
              d="m 70,67 h -40 c 0,0 -7.5,-0.802118 -7.5,-8.365747 0,-7.563629 7.5,-8.634253 7.5,-8.634253 h 20" />
      </svg>
    </button>
  )
}

export interface HamburgerButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Indicates whether the button is currently active (clicked).
   */
  active?: boolean
  /**
   * A callback that will be fired when the button is clicked.
   * This callback is generally used to toggle the state of the component.
   */
  onClick?: React.MouseEventHandler<HTMLButtonElement>
}

export default HamburgerButton
