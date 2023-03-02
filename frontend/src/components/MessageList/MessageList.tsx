import React, { type FC, useEffect, useRef } from 'react'
import { type Message } from '@models/Message'
import MessageBox from '@components/MessageBox'
import LoadingLabel from '@components/LoadingLabel'
import { type CommonProps } from '@models/commons'
import clsx from 'clsx'

import style from './MessageList.module.scss'

/**
 * Displays a list of chat messages.
 * Automatically scrolls to the bottom when new messages are added.
 */
const MessageList: FC<MessageListProps> = ({ messages, isLoading, className, ...rest }) => {
  const classList = clsx(style.messages, className)
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

  return (
    <div className={classList} {...rest} ref={elRef}>
      <div className={style.messageList}>
        {messages.map((message) => (
          <MessageBox key={message.id} text={message.text} sender={message.sender} />
        ))}
      </div>
      {isLoading && (<LoadingLabel className={style.thinking}>Cheshire cat is thinking</LoadingLabel>)}
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
}

export default React.memo(MessageList)
