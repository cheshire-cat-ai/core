import React, { type FC, type PropsWithChildren } from 'react'
import config, { type Config } from '../../config'

/**
 * FeatureGuard is a component that renders its children only if the provided feature is enabled.
 * It is used to display content conditionally based on the features enabled in the app's config.
 * If no feature is provided, the component will always render its children.
 */
const FeatureGuard: FC<FeatureGuardProps> = ({ feature, children }) => {
  const hasFeature = feature ? config.features.includes(feature) : true

  return hasFeature ? <>{children}</> : null
}

export interface FeatureGuardProps extends PropsWithChildren {
  feature?: Config['features'][number]
}

export default React.memo(FeatureGuard)
