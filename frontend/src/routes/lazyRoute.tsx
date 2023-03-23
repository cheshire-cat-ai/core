import React from 'react'

/**
 * Lazy loads a route component using React.lazy.
 * Provide the path to the component as a string, and it will be imported.
 */
const lazyRoute = (path: string) => {
  const Route = React.lazy(() => import(path))

  return (
    <React.Suspense fallback={<div>Loading...</div>}>
      <Route />
    </React.Suspense>
  )
}

export default lazyRoute
