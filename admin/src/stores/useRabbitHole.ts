import type { FileUploaderState } from '@stores/types'
import { getErrorMessage } from '@utils/errors'
import { useNotifications } from '@stores/useNotifications'
import RabbitHoleService from '@services/RabbitHole'
import { uniqueId } from '@utils/commons'

export const useRabbitHole = defineStore('rabbitHole', () => {
  const currentState = reactive<FileUploaderState>({
    loading: false,
    data: undefined
  })

  const { showNotification } = useNotifications()

  const sendFile = (file: File) => {
    currentState.loading = true
    RabbitHoleService.send(file).then((data) => {
      currentState.loading = false
      currentState.data = data
    }).then(() => showNotification({
      id: uniqueId(),
      message: `File ${file.name} successfully send down the rabbit hole!`,
      type: 'success'
    })).catch((error) => {
      currentState.error = getErrorMessage(error)
    })
  }

  return {
    currentState,
    sendFile
  }
})