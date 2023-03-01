import { useCallback, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import MessagesService from '@services/messages'
import { addMessage } from '@store/messages/slice'
import { selectCurrentMessages, selectDefaultMessages, selectIsSendingMessage } from '@store/messages/selectors'
import { uniqueId } from '@utils/commons'

/**
 * A custom hook that provides the messages service to the app.
 * This hook subscribes to the messages service and dispatches the received messages to the store.
 * It also provides the dispatchMessage function, which sends a message to the messages service and dispatches it to the store.
 *
 * I'm not 100% sure this is the best way to archive this as a hook is meant to be reusable and this is not always the case,
 * but it works for now.
 * Probably in future we'll move to a more complex state management solution like Redux Observables which will probably
 * allow side effects management at a higher level.
 */
const useMessagesService = () => {
  const dispatch = useDispatch()
  const messages = useSelector(selectCurrentMessages)
  const isSending = useSelector(selectIsSendingMessage)
  const defaultMessages = useSelector(selectDefaultMessages)

  useEffect(() => {
    MessagesService.subscribe((nextMessage, why) => {
      dispatch(addMessage({
        id: uniqueId(),
        text: nextMessage,
        sender: 'bot',
        why
      }))
    })

    return MessagesService.unsubscribe
  }, [])

  const dispatchMessage = useCallback((message: string) => {
    MessagesService.send(message)

    dispatch(addMessage({
      id: uniqueId(),
      text: message,
      sender: 'user'
    }))
  }, [])

  return { messages, defaultMessages, isSending, dispatchMessage }
}

export default useMessagesService
