import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type LLMProvidersState } from '@store/llmProviders/types'
import { type LLMProviderMetaData } from '@models/LLMProviderDescriptor'
import LanguageModels from '@services/LanguageModels'

const initialState: LLMProvidersState = {
  loading: false,
  data: undefined
}

export const fetchLanguageModels = createAsyncThunk('llmProviders/fetchAll', LanguageModels.getProviders)

/**
 * The 'llmProviders' slice of the redux store.
 * It contains the state of all the available language models.
 */
const llmProviders = createSlice({
  name: 'llmProviders',
  initialState,
  reducers: {
    setSelectedLLMProvider: (state, action: PayloadAction<LLMProviderMetaData['languageModelName']>) => {
      state.selected = action.payload
    }
  },
  extraReducers: (builder) => {
    builder.addCase(fetchLanguageModels.pending, (state) => {
      state.loading = true
    })
    builder.addCase(fetchLanguageModels.fulfilled, (state, action) => {
      state.loading = false
      state.data = action.payload

      state.selected = Object.values(action.payload.schemas)[0].languageModelName
    })
    builder.addCase(fetchLanguageModels.rejected, (state, action) => {
      state.error = action.error.message
    })
  }
})

export const { setSelectedLLMProvider } = llmProviders.actions

export default llmProviders.reducer
