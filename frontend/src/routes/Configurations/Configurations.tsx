import React, { type FC } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Page from '@components/Page'
import { Button, Card } from 'antd'

import style from './Configurations.module.scss'

/**
 * Configurations component description
 */
const Configurations: FC = ({ ...rest }) => {
  const navigate = useNavigate()
  const Action = (<Button type="primary" onClick={() => navigate('provider')}>Configure</Button>)

  return (
    <Page className={style.config} {...rest}>
      <div className={style.grid}>
        <Card title="Language model provider" actions={[Action]}>
          Discover and tailor your language model to suit your specific requirements by choosing from a list of
          providers.
        </Card>
      </div>

      <Outlet />
    </Page>
  )
}

export default Configurations
