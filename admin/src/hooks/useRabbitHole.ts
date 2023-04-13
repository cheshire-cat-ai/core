import { useCallback } from 'react'
import RabbitHoleService from '@services/RabbitHole'
import { useDispatch, useSelector } from 'react-redux'
import { setError, setResponse, startSending } from '@store/fileUploader/slice'
import {
  selectFileUploadError,
  selectFileUploadIsLoading,
  selectFileUploadResponse
} from '@store/fileUploader/selectors'
import useNotifications from '@hooks/useNotifications'
import { uniqueId } from '@utils/commons'

/**
 * A custom hook that is used to send files to the rabbit hole (file-uploader service).
 */
const useRabbitHole = () => {
  const { showNotification } = useNotifications()
  const isUploading = useSelector(selectFileUploadIsLoading)
  const error = useSelector(selectFileUploadError)
  const response = useSelector(selectFileUploadResponse)
  const dispatch = useDispatch()

  /**
   * Sends a file to the rabbit hole.
   */
  const sendFile = useCallback((file: File) => {
    dispatch(startSending())

    RabbitHoleService
      .send(file)
      .then((data) => dispatch(setResponse({ data })))
      .then(() => showNotification({
        id: uniqueId(),
        message: `File ${file.name} successfully send down the rabbit hole!`,
        type: 'success'
      }))
      .catch((error) => dispatch(setError({ error })))
  }, [dispatch, showNotification])

  return { sendFile, error, isUploading, response }
}

export default useRabbitHole
