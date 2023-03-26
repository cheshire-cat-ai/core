import React from 'react'
import { type AppFeatures } from '@models/AppFeatures'
import { Navigate } from 'react-router-dom'
import getConfig from '../config'

const config = getConfig()

/**
 * Lazy loads a route component using React.lazy.
 * Provide the path to the component as a string, and it will be imported.
 */
const lazyGuardedRoute = (path: string, feature?: AppFeatures) => {
  if (feature && !config.features.includes(feature)) return <Navigate to="/" />

  const Route = React.lazy(() => import(path))

  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Route />
    </React.Suspense>
  )
}

export default lazyGuardedRoute
