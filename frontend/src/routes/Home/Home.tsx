import React, { type FC, useCallback, useState } from 'react'
import clsx from 'clsx'
import QuestionList from '@components/QuestionList'
import MessageInput from '@components/MessageInput'
import useMessagesService from '@hooks/useMessagesService'

import style from './Home.module.scss'

/**
 * Home page component
 */
const Home: FC = () => {
  const { messages, dispatchMessage, isSending, defaultMessages } = useMessagesService()
  const [nextQuestion, setNextQuestion] = useState('')

  const onQuestionClick = useCallback((question: { text: string }) => {
    setNextQuestion(question.text)
  }, [])

  const dispatchQuestion = useCallback((message: string) => {
    setNextQuestion('')
    dispatchMessage(message)
  }, [setNextQuestion])

  console.log({ isSending, messages })

  return (
    <div className={style.home}>
      <QuestionList
        questions={defaultMessages}
        onQuestionClick={onQuestionClick}
        className={clsx(style.fadeIn, nextQuestion && style.fadeOut)}
      />
      {messages.length > 0 && (
        <section>
          {messages.map((message) => (
            <div key={message.id} className={style.message}>
              {message.sender === 'bot' ? 'Cheshire Cat: ' : 'You: '}
              {message.text}
            </div>
          ))}
        </section>
      )}
      <div className={style.inputWrapper}>
        <MessageInput placeholder="Ask the cheshire cat" value={nextQuestion} onChange={setNextQuestion} onSubmit={dispatchQuestion} />
      </div>
    </div>
  )
}

export default React.memo(Home)
