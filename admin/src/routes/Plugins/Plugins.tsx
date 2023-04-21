import React, { type FC, useEffect } from 'react'
import Page from '@components/Page/Page'
import usePlugins from '@hooks/usePlugins'
import Spinner from '@components/Spinner'
import Alert from '@components/Alert'
import Jumbotron from '@components/Jumbotron'
import { firstLetter } from '@utils/commons'

import style from './Plugins.module.scss'

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
      <Jumbotron title="Plugins" className={style.desc}>
        This page displays the list of active plugins on the Cheshire Cat.
        In the next version of the project, users will be able to activate or disable individual plugins according to their needs, allowing
        for greater customization of the user experience.
      </Jumbotron>
      {isLoading && <Spinner />}
      {error && <Alert variant="error">{error}</Alert>}
      {!isLoading &&
        !error &&
        plugins &&
        plugins.map((item) => (
          <article key={item.id} className={style.itemBox}>
            <aside>
              <div className={style.itemIcon}>
                {firstLetter(item.name)}
              </div>
            </aside>
            <div className={style.itemContent}>
              <h2>{item.name}</h2>
              {item.description}
            </div>
          </article>
        ))}
    </Page>
  )
}

export default Plugins
