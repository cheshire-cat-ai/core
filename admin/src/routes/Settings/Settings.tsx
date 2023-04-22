import React, { type FC } from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import Page from '@components/Page'
import { Button, Card } from 'antd'
import routesDescriptor from '@routes/routesDescriptor'
import Jumbotron from '@components/Jumbotron'

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
      <Jumbotron title="Set up your cat" className={style.desc}>
        Configure your Cheshire Cat to suit your needs
      </Jumbotron>

      <div className={style.grid}>
        <Card title="Language model" actions={[LLMActions]}>
          Choose and configure your favourite Large Language Model
        </Card>
        <Card title="Embedder" actions={[EmbedderActions]}>
          Choose a language embedder to help the Cat remember conversations and documents
        </Card>
      </div>
      <Outlet />
    </Page>
  )
}

export default Settings
