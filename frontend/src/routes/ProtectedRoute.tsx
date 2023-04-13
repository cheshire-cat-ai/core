import { type FC, type PropsWithChildren } from 'react'
import { type AppFeatures } from '@models/AppFeatures'
import config from '../config'

const ProtectedRoute: FC<ProtectedRouteProps> = ({ children, feature }) => {
  if (!feature) return children as JSX.Element
  if (!config.features.includes(feature)) {
    throw new Error('Page not found')
  }

  return children as JSX.Element
}

export interface ProtectedRouteProps extends PropsWithChildren {
  feature?: AppFeatures
}

export default ProtectedRoute
