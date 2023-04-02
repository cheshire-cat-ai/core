import React, { type FC, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import SidePanel from '@components/SidePanel'

import style from './LLMProvider.module.scss'

/**
 * Language Model provider page
 */
const LLMProvider: FC = () => {
  const navigate = useNavigate()
  const title = 'Configure your language model'

  const handleOnClose = useCallback(() => {
    navigate('/configurations')
  }, [navigate])

  return (
    <SidePanel active title={title} onClose={handleOnClose} position="right" className={style.llmProvider}>
      Language model provider
    </SidePanel>
  )
}

export default LLMProvider
