import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from './Scaffold'
import routesDescriptor from '@routes/routesDescriptor'

const Home = React.lazy(() => import('./Home'))
const Settings = React.lazy(() => import('./Settings'))
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
        path: routesDescriptor.home.path,
        index: true,
        element: <Home />
      },
      {
        path: routesDescriptor.settings.path,
        element: <Settings />,
        children: [
          {
            path: routesDescriptor.llm.path,
            element: <LangModelProvider />
          }
        ]
      },
      {
        path: routesDescriptor.plugins.path,
        element: <WorkInProgress />
      },
      {
        path: routesDescriptor.llm.path,
        element: <WorkInProgress />
      }
    ]
  }
])
