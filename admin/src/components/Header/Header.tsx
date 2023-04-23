import React, { type FC } from 'react'
import clsx from 'clsx'
import useToggle from 'beautiful-react-hooks/useToggle'
import { Link } from 'react-router-dom'
import Logo from '@components/Logo'
import HamburgerButton from '@components/HamburgerButton'
import Navigation from '@components/Navigation'
import { type CommonProps } from '@models/commons'

import style from './Header.module.scss'

/**
 * The application's header.
 * Contains the application's logo and a hamburger button to toggle the slide-in panel on mobile devices.
 */
const Header: FC<HeaderProps> = ({ onLogoClick, className, ...rest }) => {
  const [sideNavActive, toggleSideNave] = useToggle()
  const classList = clsx(style.header, className)

  return (
    <>
      <header className={classList} {...rest}>
        <div className={style.content}>
          <div className={clsx(style.logoWrapper)} onClick={onLogoClick} role="button">
            <Link to="/">
              <Logo />
              <p>Cheshire Cat</p>
            </Link>
          </div>
          <div className={style.actions}>
            <HamburgerButton active={sideNavActive} onClick={toggleSideNave} className={style.hmgBtn} />
            <Navigation className={style.desktopNav} />
          </div>
        </div>
      </header>
      <aside className={clsx(style.slideInNav, sideNavActive && style.active)}>
        <Navigation variant="vertical" className={style.mobileNav} />
      </aside>
    </>
  )
}

export interface HeaderProps extends CommonProps {
  onLogoClick?: () => void
}

export default Header
