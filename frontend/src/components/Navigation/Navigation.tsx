import React, { type FC } from 'react'
import clsx from 'clsx'
import { NavLink } from 'react-router-dom'
import { type CommonProps } from '@models/commons'
import { AppFeatures } from '@models/AppFeatures'
import FeatureGuard from '@components/FeatureGuard'

import style from './Navigation.module.scss'

const defaultLinks = [
  { to: '/', label: 'Chat' },
  { to: '/plugins', label: 'Plugins', guard: AppFeatures.Plugins },
  { to: '/configurations', label: 'Configurations', guard: AppFeatures.Plugins },
  { to: '/documentation', label: 'Documentation' }
]

/**
 * Displays the application's navigation
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
        {links.map(({ to, label, guard }) => (
          <FeatureGuard key={to} feature={guard}>
            <li>
              <NavLink to={to} className={({ isActive }) => isActive ? style.active : ''}>
                {label}
              </NavLink>
            </li>
          </FeatureGuard>
        ))}
      </ul>
    </nav>
  )
}

export interface NavigationProps extends CommonProps {
  links?: Array<{ to: string, label: string, guard?: AppFeatures }>
  variant?: 'vertical' | 'horizontal'
}

export default Navigation
