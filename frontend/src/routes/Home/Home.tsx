import React, { type FC, useCallback, useState } from 'react'
import DefaultMessagesList from '@components/DefaultMessagesList'
import MessageInput from '@components/MessageInput'
import useMessagesService from '@hooks/useMessagesService'
import MessageList from '@components/MessageList'

import style from './Home.module.scss'

/**
 * Displays the chat interface.
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, defaultMessages } = useMessagesService()
  const [nextMessage, setNextMessage] = useState('')

  const onQuestionClick = useCallback((question: string) => {
    const message = `${nextMessage} ${question}`.trim()
    setNextMessage(message)
  }, [nextMessage])

  const dispatchQuestion = useCallback((message: string) => {
    setNextMessage('')
    dispatchMessage(message)
  }, [dispatchMessage])

  return (
    <div className={style.home}>
      <section role="document" className={style.messagesWrapper}>
        {messages.length === 0 && (
          <DefaultMessagesList messages={defaultMessages} onMessageClick={onQuestionClick} />
        )}
        {messages.length > 0 && (
          <MessageList messages={messages} isLoading={isSending} className={style.messageList} />
        )}
      </section>
      <section className={style.inputWrapper}>
        <MessageInput value={nextMessage} onChange={setNextMessage} onSubmit={dispatchQuestion} className={style.input} />
      </section>
    </div>
  )
}

export default React.memo(Home)
