import React, { type FC } from 'react'
import { Remarkable } from 'remarkable'
import { linkify } from 'remarkable/linkify'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'
import { type Message } from '@models/Message'

import style from './MessageBox.module.scss'

const markdown = new Remarkable({ linkify: true, breaks: true, typographer: true }).use(linkify)
markdown.inline.ruler.enable(['sup', 'sub'])
markdown.core.ruler.enable(['abbr'])
markdown.block.ruler.enable(['footnote', 'deflist'])

/**
 * Displays a single chat message.
 * It is used to display both the user's messages and the Cheshire Cat's responses.
 */
const MessageBox: FC<MessageBoxProps> = ({ text, sender, className, ...rest }) => {
  const isBot = sender === 'bot'
  const classList = clsx(style.message, isBot ? style.bot : style.user, className)

  return (
    <article className={classList} {...rest}>
      {isBot && (<span className={style.label}>😺</span>)}
      <span className={style.content}>
        <span dangerouslySetInnerHTML={{ __html: markdown.render(text) }} />
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
