import React, { type FC, useState } from 'react'

import style from './Home.module.scss'

const questions = [
  { id: 0, text: 'What\'s up?' },
  { id: 1, text: 'Who\'s the Queen of Hearts?' },
  { id: 2, text: 'Where is the white rabbit?' },
  { id: 3, text: 'What is Python?' },
  { id: 4, text: 'How do I write my own AI app?' },
  { id: 5, text: 'Does pineapple belong on pizza?' }
]

/**
 * Home page component
 */
const Home: FC = () => {
  const [question, setQuestion] = useState('')

  return (
    <div className={style.home}>
      <div className={style.questions}>
        {questions.map(({ id, text }) => (
          <button role="button" key={id} className={style.question} onClick={() => setQuestion(text)}>
            {text}
          </button>
        ))}
      </div>

      <div className={style.inputWrapper}>
        <input placeholder="Ask the cheshire cat" value={question} />
      </div>
    </div>
  )
}

export default React.memo(Home)
