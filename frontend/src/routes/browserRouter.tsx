import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from '@components/Scaffold'

import Home from './Home'
import Chat from './Chat'

/**
 * Creates and exports the application routes.
 * Please check react-router-dom documentation before changing anything here
 */
export default createBrowserRouter([
  {
    path: '/',
    element: <Scaffold />,
    errorElement: <p>Error </p>,
    children: [
      {
        path: '/',
        element: <Home />
      },
      {
        path: '/chat',
        element: <Chat />
      }
    ]
  }
])
