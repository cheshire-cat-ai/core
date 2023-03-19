import React, { type FC, type HTMLAttributes, useRef } from 'react'
import useLongPress from 'beautiful-react-hooks/useLongPress'
import clsx from 'clsx'
import MicIcon from './mic.svg'

import style from './RecordingButton.module.scss'
import useAudio from 'beautiful-react-hooks/useAudio'

/**
 * RecordingButton description
 */
const RecordingButton: FC<RecordingButtonProps> = (props) => {
  const { onRecordingStart, onRecordingComplete, playAudio = true, className, ...rest } = props
  const [, { play: stayStart }] = useAudio('start-rec.mp3')
  const ref = useRef(null)
  const { isLongPressing, onLongPressEnd, onLongPressStart } = useLongPress(ref)
  const classList = clsx(style.recBtn, isLongPressing && style.active, className)

  onLongPressStart(() => {
    if (onRecordingStart) {
      onRecordingStart()

      if (playAudio) {
        stayStart()
      }
    }
  })

  onLongPressEnd(() => {
    if (onRecordingComplete) {
      onRecordingComplete('foo')
    }
  })

  return (
    <button role="button" className={classList} ref={ref} {...rest}>
      <MicIcon />
    </button>
  )
}

export interface RecordingButtonProps extends Omit<HTMLAttributes<HTMLButtonElement>, 'onClick' | 'onMouseDown'> {
  playAudio?: boolean
  onRecordingStart?: () => void
  onRecordingComplete?: (recorded: string) => void
}

export default React.memo(RecordingButton)
