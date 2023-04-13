import React, { type FC } from 'react'
import clsx from 'clsx'
import { NavLink } from 'react-router-dom'
import routesDescriptor, { type RoutesDescriptor } from '@routes/routesDescriptor'
import { type CommonProps } from '@models/commons'
import FeatureGuard from '@components/FeatureGuard'

import style from './Navigation.module.scss'

const defaultLinks: RoutesDescriptor[] = [
  routesDescriptor.home,
  routesDescriptor.plugins,
  routesDescriptor.settings,
  routesDescriptor.documentation
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
        {links.map(({ path, label, guard, external }) => (
          <FeatureGuard key={path} feature={guard}>
            <li>
              <NavLink
                to={path}
                className={({ isActive }) => isActive ? style.active : ''}
                target={external ? '_blank' : undefined}
              >
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
  links?: RoutesDescriptor[]
  variant?: 'vertical' | 'horizontal'
}

export default Navigation
