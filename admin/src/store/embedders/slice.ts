import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import EmbeddersService from '@services/EmbeddersService'
import { type EmbeddersState } from '@store/embedders/types'

const initialState: EmbeddersState = {
  loading: false,
  updating: false,
  settings: {},
  data: undefined
}

/**
 * Async thunk that fetches the available embedders from the EmbeddersService service.
 */
export const fetchEmbedders = createAsyncThunk('embedders/fetchAll', EmbeddersService.getEmbedders)

/**
 * The 'languageModels' slice of the redux store.
 * It contains the state of all the available language models.
 */
const embedders = createSlice({
  name: 'embedders',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchEmbedders.pending, (state) => {
      state.loading = true
    })
    builder.addCase(fetchEmbedders.fulfilled, (state, action) => {
      state.loading = false
      state.data = action.payload

      state.selected = state.data.selected_configuration ?? Object.values(action.payload.schemas)[0].languageModelName
      state.settings = state.data.settings.reduce((acc, { name, value }) => ({ ...acc, [name]: value }), {})
    })
    builder.addCase(fetchEmbedders.rejected, (state, action) => {
      state.error = action.error.message
    })
  }
})

export default embedders.reducer
