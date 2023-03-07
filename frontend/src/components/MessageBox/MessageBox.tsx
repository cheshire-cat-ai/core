import React, { type FC } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'
import { type Message } from '@models/Message'

import style from './MessageBox.module.scss'

/**
 * Displays a single chat message.
 * It is used to display both the user's messages and the Cheshire Cat's responses.
 */
const MessageBox: FC<MessageBoxProps> = ({ text, sender, className, ...rest }) => {
  const isBot = sender === 'bot'
  const classList = clsx(style.message, isBot ? style.bot : style.user, className)

  return (
    <article className={classList} {...rest}>
      {isBot && (<p className={style.label}>Cheshire cat says:</p>)}
      {text.split('\n').map((line, i) => <span key={i}>{line}<br /></span>)}
    </article>
  )
}

export interface MessageBoxProps extends CommonProps {
  /**
   * Message to display
   */
  text: string
  /**
   * Message sender
   */
  sender?: Message['sender']
}

export default React.memo(MessageBox)
