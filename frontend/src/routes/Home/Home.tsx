import React, { type FC, useCallback, useState } from 'react'
import DefaultMessagesList from '@components/DefaultMessagesList'
import MessageList from '@components/MessageList'
import MessageInput from '@components/MessageInput'
import LoadingLabel from '@components/LoadingLabel'
import Alert from '@components/Alert'
import useMessagesService from '@hooks/useMessagesService'

import style from './Home.module.scss'

/**
 * Displays the chat interface and handles the user's input.
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, error, defaultMessages, isReady } = useMessagesService()
  const [inputVal, setInputVal] = useState('')
  const inputDisabled = isSending || !isReady

  /**
   * When the user clicks on a default message, it will be appended to the input value state
   */
  const onQuestionClick = useCallback((question: string) => {
    const message = `${inputVal} ${question}`.trim()
    setInputVal(message)
  }, [inputVal])

  /**
   * Dispatches the user's message to the service.
   */
  const sendMessage = useCallback((message: string) => {
    setInputVal('')
    dispatchMessage(message)
  }, [dispatchMessage])

  return (
    <div className={style.home}>
      {/* The chat interface is only displayed when the service is ready */}
      {!isReady && (
        <>
          {!error && <LoadingLabel>Getting ready</LoadingLabel>}
          {error && <Alert variant="error">{error}</Alert>}
        </>
      )}
      {isReady && (
        <>
          {messages.length === 0 && (<DefaultMessagesList messages={defaultMessages} onMessageClick={onQuestionClick} />)}
          {messages.length > 0 && (<MessageList messages={messages} isLoading={isSending} error={error} className={style.messages} />)}
        </>
      )}
      <MessageInput value={inputVal} onChange={setInputVal} onSubmit={sendMessage} disabled={inputDisabled} className={style.input} />
    </div>
  )
}

export default React.memo(Home)
