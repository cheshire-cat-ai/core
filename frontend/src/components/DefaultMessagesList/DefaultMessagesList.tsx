import React, { type FC, type HTMLAttributes } from 'react'
import clsx from 'clsx'

import style from './DefaultMessagesListList.module.scss'

/**
 * Displays the provided list of messages in a different fashion.
 * This component is used to display the list of default messages.
 */
const DefaultMessagesList: FC<DefaultMessagesListProps> = (props) => {
  const { messages, onMessageClick, className, ...rest } = props
  const classList = clsx(style.defaultMessages, className)

  return (
    <div className={classList} {...rest}>
      {messages.map((message) => (
        <button role="button" key={message} className={style.message} onClick={() => onMessageClick(message)}>
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
