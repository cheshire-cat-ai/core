import React, { type FC } from 'react'
import clsx from 'clsx'
import { NavLink } from 'react-router-dom'
import { type CommonProps } from '@models/commons'

import style from './Navigation.module.scss'

const defaultLinks = [
  { to: '/', label: 'Chat' },
  { to: '/memory', label: 'Memory' },
  { to: '/configurations', label: 'Configurations' },
  { to: '/documentation', label: 'Documentation' }
]

/**
 * Navigation component description
 */
const Navigation: FC<NavigationProps> = (props) => {
  const { className, variant = 'horizontal', links = defaultLinks, ...rest } = props
  const classList = clsx(style.nav, {
    [style.vertical]: !variant || variant === 'vertical',
    [style.horizontal]: variant === 'horizontal'
  }, className)

  return (
    <nav className={classList} {...rest}>
      <ul>
        {links.map(({ to, label }) => (
          <li key={to}>
            <NavLink to={to} className={({ isActive }) => isActive ? style.active : ''}>
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}

export interface NavigationProps extends CommonProps {
  links?: Array<{ to: string, label: string }>
  variant?: 'vertical' | 'horizontal'
}

export default Navigation
