import React, { type FC, type HTMLAttributes } from 'react'
import clsx from 'clsx'
import { type MessageBase } from '@models/Message'

import style from './QuestionList.module.scss'

/**
 * Displays the list of provided questions
 */
const QuestionList: FC<QuestionListProps> = ({ questions, onQuestionClick, className, ...rest }) => {
  const classList = clsx(style.questions, className)

  return (
    <div className={classList} {...rest}>
      {questions.map((question) => (
        <button role="button" key={question.id} className={style.question} onClick={() => onQuestionClick(question)}>
          {question.text}
        </button>
      ))}
    </div>
  )
}

export interface QuestionListProps extends HTMLAttributes<HTMLElement> {
  /**
   * List of questions to display
   */
  questions: MessageBase[]
  /**
   *  Callback function to be called when a question is clicked
   * @param question
   */
  onQuestionClick: (question: MessageBase) => void
}

export default React.memo(QuestionList)
