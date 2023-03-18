import React, { type FC, useCallback, useEffect, useState } from 'react'
import DefaultMessagesList from '@components/DefaultMessagesList'
import MessageList from '@components/MessageList'
import MessageInput from '@components/MessageInput'
import LoadingLabel from '@components/LoadingLabel'
import Alert from '@components/Alert'
import RecordingButton from '@components/RecordingButton'
import useMessagesService from '@hooks/useMessagesService'
import useRabbitHole from '@hooks/useRabbitHole'
import useSpeechRecognition from '@hooks/useSpeechRecognition'

import style from './Home.module.scss'

/**
 * Displays the chat interface and handles the user's input.
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, error, defaultMessages, isReady } = useMessagesService()
  const { sendFile, isUploading } = useRabbitHole()
  const { isRecording, transcript, startRecording, stopRecording } = useSpeechRecognition()
  const [userMessage, setUserMessage] = useState('')
  const inputDisabled = isSending || isRecording || !isReady || Boolean(error)

  /**
   * The user's voice message transcript gets updated, it updates the user message state too
   */
  useEffect(() => {
    if (transcript) {
      setUserMessage(transcript)
    }
  }, [transcript])

  /**
   * When the user clicks on a default message, it will be appended to the input value state
   */
  const onQuestionClick = useCallback((question: string) => {
    const message = `${userMessage} ${question}`.trim()
    setUserMessage(message)
  }, [userMessage])

  /**
   * Dispatches the user's message to the service.
   */
  const sendMessage = useCallback((message: string) => {
    setUserMessage('')
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
      <div className={style.bottomToolbar}>
        <MessageInput
          value={userMessage}
          onChange={setUserMessage}
          onUpload={sendFile}
          onSubmit={sendMessage}
          disabled={inputDisabled}
          isUploading={isUploading}
          placeholder={generatePlaceholder(isSending, isRecording)}
          className={style.input}
        />
        <RecordingButton onRecordingStart={startRecording} onRecordingComplete={stopRecording} />
      </div>
    </div>
  )
}

/**
 * Generates a placeholder for the input based on the current state.
 */
const generatePlaceholder = (isLoading: boolean, isRecording: boolean) => {
  if (isLoading) return 'Cheshire cat is thinking...'
  if (isRecording) return 'Cheshire cat is listening...'

  return 'Ask the Cheshire cat...'
}

export default React.memo(Home)
