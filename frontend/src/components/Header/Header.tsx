import React, { type FC } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'
import Logo from '@components/Logo'
import HamburgerButton from '@components/HamburgerButton'
import Navigation from '@components/Navigation'

import style from './Header.module.scss'

/**
 * The application's header.
 * Contains the application's logo and a hamburger button to toggle the slide-in panel on mobile devices.
 */
const Header: FC<HeaderProps> = ({ active, onToggle, className, ...rest }) => {
  const classList = clsx(style.header, className)

  return (
    <header className={classList} {...rest}>
      <div className={style.content}>
        <div className={style.logoWrapper}>
          <Logo />
        </div>
        <div className={style.actions}>
          <HamburgerButton active={active} onClick={onToggle} className={style.hmgBtn} />
          <Navigation className={style.navigation} />
        </div>
      </div>
    </header>
  )
}

export interface HeaderProps extends CommonProps {
  /**
   * Whether the hamburger button is active or not.
   */
  active?: boolean
  /**
   * The function to be called when the hamburger button is clicked.
   */
  onToggle?: React.MouseEventHandler<HTMLButtonElement>
}

export default Header
