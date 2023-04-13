import React from 'react'
import ReactDOM from 'react-dom/client'
import { Provider as ReduxProvider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'

import router from '@routes/browserRouter'
import store from '@store/index'

import 'antd/dist/antd.css'
import './theme/index.scss'

/**
 * Well well well, if it isn't the root component of this application. You're looking quite rendered today, aren't you?
 * I must say, you really tie this whole thing together. Keep up the good work, my dear root component. 😺
 */
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <RouterProvider router={router} />
    </ReduxProvider>
  </React.StrictMode>
)
