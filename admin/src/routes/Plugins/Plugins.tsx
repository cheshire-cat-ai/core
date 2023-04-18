import React, { type FC, useEffect } from 'react'
import Page from '@components/Page/Page'

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
      <div className={style.desc}>
        This page displays the list of active plugins on the Cheshire Cat. In the next version of the project, users will be able to activate or
        disable individual plugins according to their needs, allowing for greater customization of the user experience.
      </div>
      {isLoading && <Spinner />}
      {error && <Alert variant="error">{error}</Alert>}
      {!isLoading &&
        !error &&
        plugins &&
        plugins.map((item) => (
          <div key={item.id} className={style.itemBox}>
            <div>
              <div className={style.itemTitle}>{item.name}</div>
              <div className={style.itemDesc}>{item.description}</div>
            </div>
          </div>
        ))}
    </Page>
  )
}

export default Plugins
