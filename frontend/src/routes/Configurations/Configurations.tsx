import React, { type FC } from 'react'
import Page from '@components/Page'
import { Button, Card } from 'antd'

import style from './Configurations.module.scss'

/**
 * Configurations component description
 */
const Configurations: FC = ({ ...rest }) => (
  <Page className={style.config} {...rest}>
    <div className={style.grid}>
      <Card title="Language model provider" actions={[<Button type="primary" key={0}>Configure</Button>]}>
        Discover and tailor your language model to suit your specific requirements by choosing from a list of
        providers.
      </Card>
      <Card title="Plugins" actions={[<Button type="primary" key={0}>Configure</Button>]}>
        Personalize the functionality of your language model by selecting from a range of available plugins.
      </Card>
    </div>
  </Page>
)

export default Configurations
