import React from 'react'
import { Outlet } from 'react-router-dom'
import Toolbar from '@components/Toolbar'

import style from './Scaffold.module.scss'

/**
 * Renders the primary element and utilizes the <Outlet /> component to display its child routes.
 * This component acts as a fundamental layout structure for the application, offering a consistent wrapper for rendering all child routes.
 * It's worth noting that the <Outlet /> is a component of the React Router library and can solely be used within a <Router> component.
 */
const Scaffold = () => (
  <main className={style.scaffold}>
    <Toolbar />
    <div className={style.content}>
      <Outlet />
    </div>
  </main>
)

export default React.memo(Scaffold)
