import { useCallback, useEffect, useMemo, useState } from 'react'

declare global {
  interface SpeechRecognitionEvent extends Event {
    results: SpeechRecognitionResultList
  }

  interface SpeechRecognitionPolyfill {
    // eslint-disable-next-line @typescript-eslint/no-misused-new
    new(): SpeechRecognitionPolyfill

    start: () => void
    stop: () => void
    abort: () => void
    addEventListener: (event: string, callback: (event: SpeechRecognitionEvent) => void) => void
    removeEventListener: (event: string, callback: (event: SpeechRecognitionEvent) => void) => void
  }

  interface Window {
    SpeechRecognition: SpeechRecognitionPolyfill
    webkitSpeechRecognition: SpeechRecognitionPolyfill
  }
}

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

const useSpeechRecognition = () => {
  const spInstance = useMemo(() => new SpeechRecognition(), [])
  const [isRecording, setIsRecording] = useState(false)
  const [transcript, setTranscript] = useState('')

  useEffect(() => {
    const getResults = (event: SpeechRecognitionEvent) => {
      const nextTranscript = event.results[0][0].transcript
      setTranscript(nextTranscript)
    }

    spInstance.addEventListener('result', getResults)

    return () => {
      spInstance.stop()
      spInstance.abort()
      spInstance.removeEventListener('result', getResults)
    }
  }, [spInstance])

  const startRecording = useCallback(() => {
    spInstance.start()
    setIsRecording(true)
  }, [spInstance])

  const stopRecording = useCallback(() => {
    spInstance.stop()
    setIsRecording(false)
  }, [spInstance])

  return Object.freeze({
    transcript,
    isRecording,
    startRecording,
    stopRecording
  })
}

export default useSpeechRecognition
