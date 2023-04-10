import React, { type FC } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Page from '@components/Page'
import { Button, Card } from 'antd'
import routesDescriptor from '@routes/routesDescriptor'

import style from './Settings.module.scss'

/**
 * Settings component description
 */
const Settings: FC = ({ ...rest }) => {
  const navigate = useNavigate()
  const LLMActions = (<Button type="primary" onClick={() => navigate(routesDescriptor.llm.path)}>Configure</Button>)
  const EmbedderActions = (<Button type="primary" disabled>Configure</Button>)

  return (
    <Page className={style.settings} variant="narrow" {...rest}>
      <div className={style.title}>
        Set up your cat instance
      </div>

      <div className={style.grid}>
        <Card title="Language model provider" actions={[LLMActions]}>
          Discover and tailor your language model to suit your specific requirements by choosing from a list of
          providers.
        </Card>
        <Card title="Embedder" actions={[EmbedderActions]}>
          Discover and tailor your language model to suit your specific requirements by choosing from a list of
          providers.
        </Card>
      </div>
      <Outlet />
    </Page>
  )
}

export default Settings
