import React, { type FC } from 'react'
import Page from '@components/Page'

import styles from './Configurations.module.scss'

/**
 * Configurations component description
 */
const Configurations: FC = ({ ...rest }) => (
  <Page className={styles.config} {...rest}>
    Hello, Configuration
  </Page>
)

export default Configurations
