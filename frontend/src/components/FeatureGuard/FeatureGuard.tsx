import React, { type FC, type PropsWithChildren } from 'react'
import getConfig, { type Config } from '../../config'

/**
 * FeatureGuard is a component that renders its children only if the provided feature is enabled.
 * It is used to display content conditionally based on the features enabled in the app's config.
 */
const FeatureGuard: FC<FeatureGuardProps> = ({ feature, children }) => {
  const config = getConfig()
  const hasFeature = config.features.includes(feature)

  return hasFeature ? <>{children}</> : null
}

export interface FeatureGuardProps extends PropsWithChildren {
  feature: Config['features'][number]
}

export default React.memo(FeatureGuard)
