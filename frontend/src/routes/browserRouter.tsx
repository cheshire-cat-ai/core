import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from './Scaffold'

const Home = React.lazy(() => import('./Home'))
const Configurations = React.lazy(() => import('./Configurations'))
const LangModelProvider = React.lazy(() => import('./LanguageModel'))
const WorkInProgress = React.lazy(() => import('./WorkInProgress'))

/**
 * Creates and exports the application routes.
 * Please check react-router-dom documentation before changing anything here
 */
export default createBrowserRouter([
  {
    path: '/',
    element: <Scaffold />,
    errorElement: <Scaffold.ErrorPage />,
    children: [
      {
        path: '/',
        index: true,
        element: <Home />
      },
      {
        path: '/configurations',
        element: <Configurations />,
        children: [
          {
            path: 'provider',
            element: <LangModelProvider />
          }
        ]
      },
      {
        path: '/plugins',
        element: <WorkInProgress />
      },
      {
        path: '/documentation',
        element: <WorkInProgress />
      }
    ]
  }
])
