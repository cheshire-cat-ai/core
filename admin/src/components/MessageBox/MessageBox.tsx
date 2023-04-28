import React, { type FC } from 'react'
import { Remarkable } from 'remarkable'
import { linkify } from 'remarkable/linkify'
import clsx from 'clsx'
import { type CommonProps } from '@models/commons'
import { type Message } from '@models/Message'
import hljs from 'highlight.js'

import style from './MessageBox.module.scss'
import 'highlight.js/styles/github.css'

const markdown = new Remarkable({
  breaks: true,
  typographer: true,
  highlight: function (str, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch (_) {
      }
    }

    try {
      return hljs.highlightAuto(str).value
    } catch (_) {
    }

    return '' // use external default escaping
  }
}).use(linkify)
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
      {isBot && (<div className={style.avatar}>😺</div>)}
      <span className={style.content} dangerouslySetInnerHTML={{ __html: markdown.render(text) }} />
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
