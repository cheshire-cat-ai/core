import React, { type FC } from 'react'
import Page from '@components/Page'
import Logo from '@components/Logo'

import style from './WorkInProgress.module.scss'

/**
 * Displays a work in progress message.
 * This component is used to display a message when a feature is not yet implemented.
 */
const WorkInProgress: FC = () => (
  <Page variant="narrow" className={style.wip}>
    <header>
      <Logo />
      <h1>Looks like we&apos;re working on it</h1>
    </header>
    <article className={style.content}>
      <p>
        Well, well, well, my dear curious friend! The development of the Cheshire Cat is a work in progress,
        indeed.<br />
        This means that what you see is not the final version, not by a long shot.
      </p>
      <p>Who knows what changes and improvements the future may hold?<br />
        But fret not, for our fantastic team is hard at work, day and night, to bring you the most
        puurrrrfect version of me.<br />
        So, do be patient, won&apos;t you? After all, good things come to those who wait... and grin!
      </p>
    </article>
  </Page>
)

export default WorkInProgress
