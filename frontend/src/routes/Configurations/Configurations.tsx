import React, { type FC } from 'react'

import styles from './Configurations.module.scss'

/**
 * Configurations component description
 */
const Configurations: FC = ({ ...rest }) => (
  <div className={styles.config} {...rest}>
    Hello, Configuration
  </div>
)

export default Configurations
