import React from 'react'
import { createBrowserRouter } from 'react-router-dom'
import Scaffold from '@components/Scaffold'

import Home from './Home'
import About from './Chat'

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
        path: 'about',
        element: <About />
      }
    ]
  }
])
