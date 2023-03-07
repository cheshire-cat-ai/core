import React from 'react'
import { Outlet, useRouteError } from 'react-router-dom'
import Toolbar from '@components/Toolbar'
import { EmptyReactElement } from '@utils/commons'
import { getErrorMessage } from '@utils/errors'

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

/**
 * A basic scaffold to render the error page.
 * This component is used as the errorElement prop of the <BrowserRouter /> component.
 * The reason this component has been included in the same file as the Scaffold component is because it conceptually belongs to the
 * application's Scaffold. In fact, it has been attached to the Scaffold component as a property. This is a common pattern in React
 * applications where components are attached to other components as properties either as children or because they belong to the same
 * context (it in fact uses the same styling as well)
 */
const ErrorPage = () => {
  const error = useRouteError()
  const errorMessage = getErrorMessage(error)

  return (
    <main className={style.scaffold}>
      <Toolbar title="Ops... something went wrong" ToolbarActions={EmptyReactElement} />
      <div className={style.content}>
        <h1>{errorMessage}</h1>
      </div>
    </main>
  )
}

/**
 * Attaches the ErrorPage component to the Scaffold component as a property.
 */
Scaffold.ErrorPage = ErrorPage

export default Scaffold
