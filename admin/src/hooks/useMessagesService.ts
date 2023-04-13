import { useCallback } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import useDidMount from 'beautiful-react-hooks/useDidMount'
import MessagesService from '@services/MessagesService'
import { addMessage, setError, setReady } from '@store/messages/slice'
import {
  selectCurrentMessages,
  selectError,
  selectIsReady,
  selectIsSendingMessage,
  selectRandomDefaultMessages
} from '@store/messages/selectors'
import { now, uniqueId } from '@utils/commons'
import { getErrorMessage } from '@utils/errors'

/**
 * A custom hook that provides the messages service to the app.
 * This hook subscribes to the messages service and dispatches the received messages to the store.
 * It also provides the dispatchMessage function, which sends a message to the messages service and dispatches it to
 * the store.
 *
 * I'm not 100% sure this is the best way to archive this as a hook is meant to be reusable and that is not always the
 * case here, but it works for the moment. Probably in future we'll move to a more structured state management solution
 * like Redux Observables which will probably allow side effects management at a higher level.
 */
const useMessagesService = () => {
  const dispatch = useDispatch()
  const onMount = useDidMount()
  const messages = useSelector(selectCurrentMessages)
  const isSending = useSelector(selectIsSendingMessage)
  const isReady = useSelector(selectIsReady)
  const error = useSelector(selectError)
  const defaultMessages = useSelector(selectRandomDefaultMessages)

  /**
   * Subscribes to the messages service on component mount
   * and dispatches the received messages to the store.
   * It also dispatches the error to the store if an error occurs.
   */
  onMount(() => {
    MessagesService
      .connect(() => dispatch(setReady()))
      .onMessage((message: string, why: any) => {
        dispatch(addMessage({
          id: uniqueId(),
          text: message,
          sender: 'bot',
          timestamp: now(),
          why
        }))
      })
      .onError((error: Error) => {
        const errorMessage = getErrorMessage(error)
        dispatch(setError(errorMessage))
      })

    return () => {
      MessagesService.disconnect()
    }
  })

  /**
   * Sends a message to the messages service and optimistically dispatches it to the store
   */
  const dispatchMessage = useCallback((message: string) => {
    MessagesService.send(message)

    dispatch(addMessage({
      id: uniqueId(),
      text: message.trim(),
      timestamp: now(),
      sender: 'user'
    }))
  }, [dispatch])

  return { messages, isReady, error, defaultMessages, isSending, dispatchMessage }
}

export default useMessagesService
