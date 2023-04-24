import React, { type FC, useEffect, useRef } from 'react'
import useAudio from 'beautiful-react-hooks/useAudio'
import { type Message } from '@models/Message'
import MessageBox from '@components/MessageBox'
import LoadingLabel from '@components/LoadingLabel'
import Alert from '@components/Alert'
import { type CommonProps } from '@models/commons'
import clsx from 'clsx'

import style from './MessageList.module.scss'

/**
 * Displays a list of chat messages.
 * Automatically scrolls to the bottom when new messages are added.
 */
const MessageList: FC<MessageListProps> = ({ messages, error, isLoading, className, playSound, ...rest }) => {
  const classList = clsx(style.messages, className)
  const [, { play: playPop }] = useAudio('pop.mp3')
  const elRef = useRef<HTMLDivElement>(null)

  /**
   * Scrolls to the bottom of the list when new messages are added.
   */
  useEffect(() => {
    const target = elRef.current

    if (target && messages.length > 0) {
      const lastMessageEl = target.querySelector('article:last-of-type')

      if (lastMessageEl) {
        setTimeout(() => {
          lastMessageEl?.scrollIntoView({ behavior: 'smooth' })
        }, 10)
      }
    }
  }, [messages.length])

  useEffect(() => {
    if (messages.length > 0 && playSound) {
      playPop()
    }
  }, [playPop, messages.length])

  return (
    <div className={classList} {...rest} ref={elRef}>
      <div className={style.messageList}>
        {messages.map((message) => (
          <MessageBox key={message.id} text={message.text} sender={message.sender} />
        ))}
      </div>
      {error && (<Alert variant="error" className={style.alert}>{error}</Alert>)}
      {isLoading && !error && (<LoadingLabel className={style.thinking}>😺 Cheshire cat is thinking</LoadingLabel>)}
    </div>
  )
}

export interface MessageListProps extends CommonProps {
  /*
   * The list of messages to display
   */
  messages: Message[]
  /**
   * Whether the list is loading
   */
  isLoading?: boolean
  /**
   * The error message to display
   */
  error?: string

  /**
   * Whether to play a sound when a new message is added
   */
  playSound?: boolean
}

export default React.memo(MessageList)
