import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import lazyGuardedRoute from '@routes/lazyGuardedRoute'
import { AppFeatures } from '@models/AppFeatures'
import Scaffold from './Scaffold'

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
        element: lazyGuardedRoute('./Home')
      },
      {
        path: '/configurations',
        element: lazyGuardedRoute('./Configurations', AppFeatures.Configurations)
      },
      {
        path: '/memory',
        element: lazyGuardedRoute('./WorkInProgress', AppFeatures.MemoryManagement)
      },
      {
        path: '/documentation',
        element: lazyGuardedRoute('./WorkInProgress')
      }
    ]
  }
])
