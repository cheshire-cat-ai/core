import React, { type FC, useCallback, useState } from 'react'
import DefaultMessagesList from '@components/DefaultMessagesList'
import MessageList from '@components/MessageList'
import MessageInput from '@components/MessageInput'
import useMessagesService from '@hooks/useMessagesService'

import style from './Home.module.scss'

/**
 * Displays the chat interface.
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, defaultMessages } = useMessagesService()
  const [userMessage, setUserMessage] = useState('')

  const onQuestionClick = useCallback((question: string) => {
    const message = `${userMessage} ${question}`.trim()
    setUserMessage(message)
  }, [userMessage])

  const sendMessage = useCallback((message: string) => {
    setUserMessage('')
    dispatchMessage(message)
  }, [dispatchMessage])

  return (
    <div className={style.home}>
      {messages.length === 0 && (<DefaultMessagesList messages={defaultMessages} onMessageClick={onQuestionClick} />)}
      {messages.length > 0 && (<MessageList messages={messages} isLoading={isSending} className={style.messages} />)}
      <MessageInput value={userMessage} onChange={setUserMessage} onSubmit={sendMessage} disabled={isSending} className={style.input} />
    </div>
  )
}

export default React.memo(Home)
