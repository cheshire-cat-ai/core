import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import lazyRoute from '@routes/lazyRoute'
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
        element: lazyRoute('./Home')
      },
      {
        path: '/configuration',
        element: lazyRoute('./Configuration')
      }
    ]
  }
])
