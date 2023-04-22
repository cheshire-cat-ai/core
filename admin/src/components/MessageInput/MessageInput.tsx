import React, { type FC, type HTMLAttributes, useCallback, useEffect, useRef, useState } from 'react'
import Spinner from '@components/Spinner'
import clsx from 'clsx'
import AttachmentIcon from './paperclip.svg'
import SendIcon from './send.svg'
import FeatureGuard from '@components/FeatureGuard/FeatureGuard'
import { AppFeatures } from '@models/AppFeatures'

import style from './MessageInput.module.scss'
import { Message } from '@models/Message'

/**
 * A stateless input component for input chat messages.
 * It has a textarea for the message and a submit button as well as an attachment button to upload files.
 */
const MessageInput: FC<ChatInputProps> = (props) => {
  const { messages ,value, onChange, onSubmit, onUpload, disabled, isUploading, className, ...rest } = props
  const [isTwoLines, setIsTwoLines] = useState(false)
  const classList = clsx(style.messageInput, isTwoLines && style.bigger, className)
  const textAreaRef = useRef<HTMLTextAreaElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  /**
   * Checks if the textarea needs to be multiline and updates the state accordingly.
   */
  useEffect(() => {
    const target = textAreaRef.current

    if (target && !value) {
      setIsTwoLines(false)
    }

    if (target && value) {
      const letterWidth = 7.95
      const isMultiLine = letterWidth * value.length > target.offsetWidth
      const hasLineBreak = !!(/\r|\n/.exec(value))

      setIsTwoLines(isMultiLine || hasLineBreak)
    }
  }, [value])

  /**
   * Handles form submit by calling the onSubmit callback if it exists.
   * It also prevents the default form submit behavior.
   */
  const handleSubmit = useCallback((event: React.FormEvent) => {
    event.preventDefault()

    if (onSubmit && value) {
      setIsTwoLines(false)
      onSubmit(value)
    }
  }, [value, onSubmit])

  /**
   * Handles textarea change by calling the onChange callback,
   * makes sure to prevent the default behavior.
   */
  const handleChange = useCallback((event: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { value } = event.target
    event.preventDefault()

    onChange(value)
  }, [onChange])

  /**
   * Handles textarea keydown by calling the onSubmit callback if it exists.
   */
  const handleKeydown = useCallback((event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    const { key, keyCode } = event
    const isEnter = key === 'Enter' || keyCode === 13
    const isShiftKey = event.shiftKey

    if (isEnter && !isShiftKey && onSubmit && value) {
      event.preventDefault()
      onSubmit(value)
      setIsTwoLines(false)
    }
  }, [value, onSubmit])

  /**
   * Handles the file upload button click by triggering the file input click.
   */
  const onFileUploadClick = useCallback(() => {
    const target = inputRef.current

    if (target) {
      target.click()
    }
  }, [])

  /**
   * Handles the file upload change by calling the onUpload callback if it exists.
   */
  const onFileUploadChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files ? event.target.files[0] : null

    if (file && onUpload) {
      onUpload(file)

      event.target.form?.reset()
    }
  }, [onUpload])

  useEffect(() => {
    if (messages.length != 0 || messages.length %2 == 1 ) {
      textAreaRef.current?.focus();
    }
  }, [messages.length])


  return (
      <form className={classList} onSubmit={handleSubmit}>
      <textarea
        value={value}
        name="message"
        onChange={handleChange}
        onKeyDown={handleKeydown}
        disabled={disabled}
        ref={textAreaRef}
        {...rest}
      />
      <input type="file" ref={inputRef} accept="text/plain, text/markdown, application/pdf, .md" onChange={onFileUploadChange} />
      <button type="submit" disabled={!value || value.length === 0}>
        <SendIcon />
      </button>
      <FeatureGuard feature={AppFeatures.FileUpload}>
        {isUploading && (<Spinner size={22} />)}
        {!isUploading && (
          <button type="button" onClick={onFileUploadClick} disabled={disabled}>
            <AttachmentIcon />
          </button>
        )}
      </FeatureGuard>
    </form>
    
  )
}

export interface ChatInputProps extends Omit<HTMLAttributes<HTMLTextAreaElement>, 'onChange' | 'onSubmit'> {
  messages: Message[]
  value: string
  onChange: (nextValue: string) => void
  onSubmit?: (nextValue: string) => void
  onUpload?: (file: File) => void
  isUploading?: boolean
  disabled?: boolean
}

export default React.memo(MessageInput)
