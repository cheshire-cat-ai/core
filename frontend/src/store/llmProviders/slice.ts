import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type LLMProvidersState } from '@store/llmProviders/types'
import { type LLMProviderMetaData } from '@models/LLMProviderDescriptor'
import LanguageModels from '@services/LanguageModels'
import { type LLMSettings } from '@models/LLMSettings'

const initialState: LLMProvidersState = {
  loading: false,
  updating: false,
  data: undefined
}

export const fetchLanguageModels = createAsyncThunk('llmProviders/fetchAll', LanguageModels.getProviders)
export const updateLanguageModelSettings = createAsyncThunk(
  'llmProviders/updateOptions',
  (options: { name: string, settings: LLMSettings }) => {
    const { name, settings } = options

    return LanguageModels.setProviderOptions(name, settings)
  }
)

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

    builder.addCase(updateLanguageModelSettings.pending, (state) => {
      state.updating = true
    })

    builder.addCase(updateLanguageModelSettings.fulfilled, (state, action) => {
      state.updating = false
    })

    builder.addCase(updateLanguageModelSettings.rejected, (state, action) => {
      state.updating = false
      state.error = action.error.message
    })
  }
})

export const { setSelectedLLMProvider } = llmProviders.actions

export default llmProviders.reducer
