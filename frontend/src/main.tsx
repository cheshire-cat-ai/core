import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import { Provider as ReduxProvider } from 'react-redux'
import { RouterProvider } from 'react-router-dom'

import router from '@routes/browserRouter'
import store from '@store/index'

import './theme/index.scss'

/**
 * The Cheshire Cat currently uses Ant Design as its design system. However, we plan to replace it with a custom
 * solution that will be easier to customize. Our goal is to provide a platform that allows non-technical users to
 * easily modify the theme by tweaking CSS variables. This approach will ensure that changes are visible in real-time
 * without requiring users to modify the JavaScript file and run the build.
 */
const theme = {
  token: {
    colorPrimary: '#5C1EAE'
  }
}

/**
 * Well well well, if it isn't the root component of this application. You're looking quite rendered today, aren't you?
 * I must say, you really tie this whole thing together. Keep up the good work, my dear root component. 😺
 */
ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <ReduxProvider store={store}>
      <ConfigProvider theme={theme}>
        <RouterProvider router={router} />
      </ConfigProvider>
    </ReduxProvider>
  </React.StrictMode>
)
