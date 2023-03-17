import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from './Scaffold'

import Home from './Home'

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
        // todo: create a lazy loading utility to load the page components
        element: <Home />
      }
    ]
  }
])
