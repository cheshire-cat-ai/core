import React, { type FC, type HTMLAttributes, useRef } from 'react'
import useLongPress from 'beautiful-react-hooks/useLongPress'
import useAudio from 'beautiful-react-hooks/useAudio'
import clsx from 'clsx'
import FeatureGuard from '@components/FeatureGuard/FeatureGuard'
import { AppFeatures } from '@models/AppFeatures'
import MicIcon from './mic.svg'
import style from './RecordingButton.module.scss'


/**
 * A stateless button that records chat messages.
 */
const RecordingButton: FC<RecordingButtonProps> = (props) => {
  const { onRecordingStart, onRecordingComplete, playAudio , disabled, className, ...rest } = props
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
    <FeatureGuard feature={AppFeatures.AudioRecording}>
      <button role="button" disabled={disabled} className={classList} ref={ref} {...rest}>
        <MicIcon />
      </button>
    </FeatureGuard>
  )
}

export interface RecordingButtonProps extends Omit<HTMLAttributes<HTMLButtonElement>, 'onClick' | 'onMouseDown'> {
  playAudio?: boolean
  onRecordingStart?: () => void
  onRecordingComplete?: (recorded: string) => void
  disabled?: boolean
}

export default React.memo(RecordingButton)
