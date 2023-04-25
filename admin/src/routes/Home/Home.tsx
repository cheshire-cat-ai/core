import React, { type FC, useCallback, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import useSpeechRecognition from 'beautiful-react-hooks/useSpeechRecognition'
import clsx from 'clsx'
import DefaultMessagesList from '@components/DefaultMessagesList'
import MessageList from '@components/MessageList'
import MessageInput from '@components/MessageInput'
import LoadingLabel from '@components/LoadingLabel'
import Alert from '@components/Alert'
import Page from '@components/Page'
import RecordingButton from '@components/RecordingButton'
import useMessagesService from '@hooks/useMessagesService'
import useRabbitHole from '@hooks/useRabbitHole'
import { slideBottomInOUt } from '@utils/animations'
import style from './Home.module.scss'
import useToggle from 'beautiful-react-hooks/useToggle'
import MuteButton from '@components/MuteButton/MuteButton'

/**
 * Displays the chat interface and handles the user's input.
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, error, defaultMessages, isReady } = useMessagesService()
  const { isRecording, transcript, startRecording, stopRecording, isSupported } = useSpeechRecognition()
  const { sendFile, isUploading } = useRabbitHole()
  const [userMessage, setUserMessage] = useState('')
  const inputDisabled = isSending || isRecording || !isReady || Boolean(error)
  const [volumeEnabled, toggleVolume] = useToggle(true)
  /*
   * When the user stops recording, the transcript will be sent to the messages service
   */
  useEffect(() => {
    if (transcript === '') return
    dispatchMessage(transcript)
  }, [transcript, dispatchMessage])

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
    <Page variant="narrow" className={style.home}>
      {/* The chat interface is only displayed when the service is ready */}
      {!isReady && (
        <>
          {!error && <LoadingLabel>Getting ready</LoadingLabel>}
          {error && <Alert variant="error">{error}</Alert>}
        </>
      )}
      {isReady && (
        <>
          {messages.length === 0 && (
            <DefaultMessagesList messages={defaultMessages} onMessageClick={onQuestionClick} />)}
          {messages.length > 0 && (
            <MessageList messages={messages} isLoading={isSending} error={error} playSound={volumeEnabled} className={style.messages} />)}
        </>
      )}
      <motion.div className={clsx(style.bottomToolbar)} {...slideBottomInOUt}>
        <MuteButton active={volumeEnabled} onClick={toggleVolume} className={style.soundBtn} />
        <MessageInput
          messages={messages}
          value={userMessage}
          onChange={setUserMessage}
          onUpload={sendFile}
          onSubmit={sendMessage}
          disabled={inputDisabled}
          isUploading={isUploading}
          placeholder={generatePlaceholder(isSending, isRecording, error)}
          className={style.input}
        />
        {isSupported && (
          <RecordingButton
            onRecordingStart={startRecording}
            onRecordingComplete={stopRecording}
            disabled={inputDisabled}
            playAudio={volumeEnabled}
          />
        )}
      </motion.div>
    </Page>
  )
}

/**
 * Generates a placeholder for the input based on the current state.
 */
const generatePlaceholder = (isLoading: boolean, isRecording: boolean, error?: string) => {
  if (error) return 'Well, well, well, looks like something has gone amiss'
  if (isLoading) return 'The enigmatic Cheshire cat is pondering...'
  if (isRecording) return 'The curious Cheshire cat is all ear...'

  return 'Ask the Cheshire Cat...'
}

export default React.memo(Home)
