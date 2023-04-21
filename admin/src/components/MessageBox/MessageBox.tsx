import React, { type FC } from 'react'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'
import { type Message } from '@models/Message'
import { Remarkable } from 'remarkable'
import { linkify } from 'remarkable/linkify'

import style from './MessageBox.module.scss'


/**
 * Displays a single chat message.
 * It is used to display both the user's messages and the Cheshire Cat's responses.
 */
const MessageBox: FC<MessageBoxProps> = ({ text, sender, className, ...rest }) => {
  const isBot = sender === 'bot'
  const classList = clsx(style.message, isBot ? style.bot : style.user, className)
  const md = new Remarkable({ linkify: true, breaks: true, typographer: true }).use(linkify)
  md.inline.ruler.enable(['sup', 'sub'])
  md.core.ruler.enable(['abbr'])
  md.block.ruler.enable(['footnote', 'deflist'])

  return (
    <article className={classList} {...rest}>
      {isBot && (<span className={style.label}>😺</span>)}
      <span className={style.content}>
        <span dangerouslySetInnerHTML={{ __html: md.render(text) }} />
      </span>
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
