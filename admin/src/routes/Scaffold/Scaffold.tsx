import React, { useCallback } from 'react'
import { Outlet, useRouteError, useNavigate } from 'react-router-dom'
import { uniqueId } from '@utils/commons'
import clsx from 'clsx'
import Page from '@components/Page'
import Header from '@components/Header'
import Logo from '@components/Logo'
import NotificationStack from '@components/NotificationStack'
import PageLoadingSpinner from '@components/PageLoadingSpinner'
import { getErrorCode, getErrorMessage } from '@utils/errors'
import useNotifications from '@hooks/useNotifications'
import WittyService from '@services/WittyService'

import style from './Scaffold.module.scss'

/**
 * Renders the primary element and utilizes the <Outlet /> component to display its child routes.
 * This component acts as a fundamental layout structure for the application, offering a consistent wrapper for
 * rendering all child routes. It's worth noting that the <Outlet /> is a component of the React Router library and can
 * solely be used within a <Router> component.
 */
const Scaffold = () => {
  const { notifications, showNotification } = useNotifications()
  const navigate = useNavigate();

  const purrNotification = useCallback(() => {

    // show notification
    showNotification({
      id: uniqueId(),
      message: WittyService.catchPhrase(),
      type: 'info'
    })

    // go to home page
    navigate('/')

  }, [showNotification])

  return (
    <div className={style.scaffold}>
      <Header onLogoClick={purrNotification} />
      <main className={style.content}>
        <React.Suspense fallback={<PageLoadingSpinner />}>
          <Outlet />
        </React.Suspense>
      </main>
      <NotificationStack notifications={notifications} />
    </div>
  )
}

/**
 * A basic scaffold to render the error page.
 * This component is used as the errorElement prop of the <BrowserRouter /> component.
 * The reason this component has been included in the same file as the Scaffold component is because it conceptually
 * belongs to the application's Scaffold. In fact, it has been attached to the Scaffold component as a property. This
 * is a common pattern in React applications where components are attached to other components as properties either as
 * children or because they belong to the same context (it in fact uses the same styling as well)
 */
const ErrorPage = () => {
  const error = useRouteError()
  const errorMessage = getErrorMessage(error)
  const errorCode = getErrorCode(error)

  return (
    <div className={style.scaffold}>
      <Header />
      <main className={clsx(style.content, style.error)}>
        <Page variant="narrow">
          <header>
            <Logo />
            <h1>Hmm... it appears that something has caused a disturbance in my purr</h1>
          </header>
          <h2>{errorCode && `${errorCode}: `}{errorMessage}</h2>
        </Page>
      </main>
    </div>
  )
}

/**
 * Attaches the ErrorPage component to the Scaffold component as a property.
 */
Scaffold.ErrorPage = ErrorPage

export default Scaffold
