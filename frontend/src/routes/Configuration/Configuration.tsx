import React, { type FC } from 'react'

import styles from './Configuration.module.scss'

/**
 * Configuration component description
 */
const Configuration: FC = ({ ...rest }) => (
  <div className={styles.config} {...rest}>
    Hello, Configuration
  </div>
)

export default Configuration
