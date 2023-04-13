import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type FileUploaderState } from '@store/fileUploader/types'
import { type RabbitHoleServiceResponse } from '@services/RabbitHole'
import { getErrorMessage } from '@utils/errors'

const initialState: FileUploaderState = {
  loading: false,
  data: undefined
}

/**
 * The 'fileUploader' slice of the redux store.
 * It contains the state of the files that the user has sent to the bot.
 * It extends the AsyncStateBase interface, which defines the structure of the state of an asynchronous operation.
 */
const fileUploaderSlice = createSlice({
  name: 'fileUploader',
  initialState,
  reducers: {
    startSending: (state) => {
      state.loading = true
    },
    setResponse: (state, action: PayloadAction<{ data: RabbitHoleServiceResponse }>) => {
      state.loading = false
      state.data = action.payload.data
    },
    setError: (state, action: PayloadAction<{ error: Error }>) => {
      state.error = getErrorMessage(action.payload.error)
    }
  }
})

export const { setResponse, startSending, setError } = fileUploaderSlice.actions

export default fileUploaderSlice.reducer
