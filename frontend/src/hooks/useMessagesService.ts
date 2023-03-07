import { useCallback, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import MessagesService, { MessageServiceErrorCodes } from '@services/messages'
import { addMessage, setError, setReady, toggleLoading } from '@store/messages/slice'
import { selectCurrentMessages, selectDefaultMessages, selectError, selectIsReady, selectIsSendingMessage } from '@store/messages/selectors'
import { now, uniqueId } from '@utils/commons'
import { getErrorMessage, getErrorMessageFromErrorCodeMap } from '@utils/errors'

/**
 * A custom hook that provides the messages service to the app.
 * This hook subscribes to the messages service and dispatches the received messages to the store.
 * It also provides the dispatchMessage function, which sends a message to the messages service and dispatches it to the store.
 *
 * I'm not 100% sure this is the best way to archive this as a hook is meant to be reusable and that is not always the case here,
 * but it works for the moment.
 * Probably in future we'll move to a more structured state management solution like Redux Observables which will probably
 * allow side effects management at a higher level.
 */
const useMessagesService = () => {
  const dispatch = useDispatch()
  const messages = useSelector(selectCurrentMessages)
  const isSending = useSelector(selectIsSendingMessage)
  const isReady = useSelector(selectIsReady)
  const error = useSelector(selectError)
  const defaultMessages = useSelector(selectDefaultMessages)

  /**
   * Subscribes to the messages service on component mount
   * and dispatches the received messages to the store.
   * It also dispatches the error to the store if an error occurs.
   */
  useEffect(() => {
    /**
     * Dispatches the received message to the store
     */
    const onMessage = (message: string, why: any) => {
      dispatch(toggleLoading())

      dispatch(addMessage({
        id: uniqueId(),
        text: message,
        sender: 'bot',
        timestamp: now(),
        why
      }))
    }

    /**
     * Dispatches the error to the store
     */
    const onError = (error: Error) => {
      const errorCode = getErrorMessage(error)
      const errorMessage = getErrorMessageFromErrorCodeMap(MessageServiceErrorCodes, errorCode)
      dispatch(setError(errorMessage))
    }

    MessagesService.onOpen(() => dispatch(setReady()), onError)
    MessagesService.subscribe(onMessage, onError)

    return MessagesService.unsubscribe
  }, [dispatch])

  /**
   * Sends a message to the messages service and optimistically dispatches it to the store
   */
  const dispatchMessage = useCallback((message: string) => {
    MessagesService.send(message)

    dispatch(toggleLoading())

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
