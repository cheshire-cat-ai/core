import React, { type FC, type HTMLAttributes } from 'react'
import clsx from 'clsx'

import style from './DefaultMessagesList.module.scss'

/**
 * Displays a list of default messages that the user can click on to send.
 * It is used to display a list of generic questions that the user can ask
 * the Cheshire Cat.
 */
const DefaultMessagesList: FC<DefaultMessagesListProps> = (props) => {
  const { messages, onMessageClick, className, ...rest } = props
  const classList = clsx(style.defaultMessages, className)

  return (
    <div className={classList} {...rest}>
      {messages.map((message) => (
        <button key={message} role="button" onClick={() => onMessageClick(message)}>
          {message}
        </button>
      ))}
    </div>
  )
}

export interface DefaultMessagesListProps extends HTMLAttributes<HTMLElement> {
  /**
   * List of messages to display
   */
  messages: string[]
  /**
   *  Callback function to be called when a message is clicked
   * @param message
   */
  onMessageClick: (message: string) => void
}

export default React.memo(DefaultMessagesList)
