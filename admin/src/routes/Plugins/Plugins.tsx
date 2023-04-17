import React, { type FC, useEffect } from 'react'
import Page from '@components/Page/Page'
import { List } from 'antd'

import style from './Plugins.module.scss'
import usePlugins from '@hooks/usePlugins'
import Spinner from '@components/Spinner/Spinner'
import Alert from '@components/Alert/Alert'

/**
 * Plugins list component
 */
const Plugins: FC = () => {
  const { isLoading, plugins, error, requirePlugins } = usePlugins()

  useEffect(() => {
    void requirePlugins()
  }, [requirePlugins])

  return (
    <Page className={style.plugins} variant="narrow">
      <div className={style.title}>Plugins</div>
      {isLoading && <Spinner />}
      {error && <Alert variant="error">{error}</Alert>}
      {!isLoading && !error && plugins && (
        <List
          itemLayout="horizontal"
          dataSource={plugins}
          renderItem={(item, index) => (
            <List.Item>
              <List.Item.Meta title={item.name} description="Ant Design, a design language for background applications, is refined by Ant UED Team" />
            </List.Item>
          )}
        />
      )}
    </Page>
  )
}

export default Plugins
