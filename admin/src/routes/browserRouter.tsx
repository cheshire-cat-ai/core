import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from './Scaffold'
import routesDescriptor from '@routes/routesDescriptor'
import ProtectedRoute from '@routes/ProtectedRoute'
import { AppFeatures } from '@models/AppFeatures'

const Home = React.lazy(() => import('./Home'))
const Settings = React.lazy(() => import('./Settings'))
const LanguageModels = React.lazy(() => import('./LanguageModels'))
const Plugins = React.lazy(() => import('./Plugins'))
// const WorkInProgress = React.lazy(() => import('./WorkInProgress'))

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
        element: (
          <ProtectedRoute feature={AppFeatures.Settings}>
            <Settings />
          </ProtectedRoute>
        ),
        children: [
          {
            path: routesDescriptor.llm.path,
            element: <LanguageModels />
          }
        ]
      },
      {
        path: routesDescriptor.plugins.path,
        element: (
          <ProtectedRoute feature={AppFeatures.Plugins}>
            <Plugins />
          </ProtectedRoute>
        )
      }
    ]
  }
])
