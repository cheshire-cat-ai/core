import React, { type FC } from 'react'

import style from './LLMProvider.module.scss'
import SlidePanel from '@components/SlidePanel'

/**
 * Language Model provider page
 */
const LLMProvider: FC = () => {
  return (
    <SlidePanel active variant="from-right" className={style.provider}>
      Language model provider
    </SlidePanel>
  )
}

export default LLMProvider
