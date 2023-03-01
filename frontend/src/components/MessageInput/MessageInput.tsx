import React, { type ChangeEvent, type FC, type FormEvent, type HTMLAttributes, type KeyboardEvent, useCallback } from 'react'
import clsx from 'clsx'

import style from './MessageInput.module.scss'

/**
 * A stateless input component allowing the user to enter a message and/or attach a file
 */
const MessageInput: FC<ChatInputProps> = ({ value, onChange, onSubmit, className, ...rest }) => {
  const classList = clsx(style.messageInput, className)

  const handleSubmit = useCallback((event: FormEvent) => {
    event.preventDefault()

    if (onSubmit) {
      onSubmit(value)
    }
  }, [value, onSubmit])

  const handleChange = useCallback((event: ChangeEvent<HTMLTextAreaElement>) => {
    const { value } = event.target
    event.preventDefault()

    onChange(value)
  }, [onChange])

  const handleKeydown = useCallback((event: KeyboardEvent<HTMLTextAreaElement>) => {
    const { key, keyCode } = event
    const isEnter = key === 'Enter' || keyCode === 13

    if (isEnter && onSubmit) {
      event.preventDefault()
      onSubmit(value)
    }
  }, [value, onSubmit])

  return (
    <form className={classList} onSubmit={handleSubmit}>
      <textarea value={value} name="message" onChange={handleChange} onKeyDown={handleKeydown} {...rest} />
      <button type="submit" disabled={!value || value.length === 0}>
        <svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 1L7 9" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M15 1L10.1 15L7.3 8.7L1 5.9L15 1Z" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      <button type="button" disabled={true}>
        <svg viewBox="0 0 22 23" xmlns="http://www.w3.org/2000/svg">
          <path
            d="M20.4383 10.6622L11.2483 19.8522C10.1225 20.9781 8.59552 21.6106 7.00334 21.6106C5.41115 21.6106 3.88418 20.9781 2.75834 19.8522C1.63249 18.7264 1 17.1994 1 15.6072C1 14.015 1.63249 12.4881 2.75834 11.3622L11.9483 2.17222C12.6989 1.42166 13.7169 1 14.7783 1C15.8398 1 16.8578 1.42166 17.6083 2.17222C18.3589 2.92279 18.7806 3.94077 18.7806 5.00222C18.7806 6.06368 18.3589 7.08166 17.6083 7.83222L8.40834 17.0222C8.03306 17.3975 7.52406 17.6083 6.99334 17.6083C6.46261 17.6083 5.95362 17.3975 5.57834 17.0222C5.20306 16.6469 4.99222 16.138 4.99222 15.6072C4.99222 15.0765 5.20306 14.5675 5.57834 14.1922L14.0683 5.71222"
            strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
    </form>
  )
}

export interface ChatInputProps extends Omit<HTMLAttributes<HTMLTextAreaElement>, 'onChange' | 'onSubmit'> {
  value: string
  onChange: (nextValue: string) => void
  onSubmit?: (nextValue: string) => void
}

export default React.memo(MessageInput)
