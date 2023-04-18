import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type LLMProvidersState } from '@store/llmProviders/types'
import { type LLMProviderMetaData } from '@models/LLMProviderDescriptor'
import LanguageModels from '@services/LanguageModels'
import { type LLMSettings } from '@models/LLMSettings'
import { toJSON } from '@utils/commons'

const initialState: LLMProvidersState = {
  loading: false,
  updating: false,
  settings: {},
  data: undefined
}

/**
 * Async thunk that fetches the available language models from the LanguageModels service.
 */
export const fetchLanguageModels = createAsyncThunk('llmProviders/fetchAll', LanguageModels.getProviders)

/**
 * Async thunk that updates the settings of a language model using the LanguageModels service.
 */
export const updateLanguageModelSettings = createAsyncThunk(
  'llmProviders/updateOptions',
  (options: { name: string, settings: LLMSettings }) => {
    const { name, settings } = options

    return LanguageModels.setProviderOptions(name, settings).then(toJSON)
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
    },
    setLLMSettings: (state, action: PayloadAction<{ name: string, settings: LLMSettings }>) => {
      const { name, settings } = action.payload

      state.settings[name] = settings
    }
  },
  extraReducers: (builder) => {
    builder.addCase(fetchLanguageModels.pending, (state) => {
      state.loading = true
    })

    builder.addCase(fetchLanguageModels.fulfilled, (state, action) => {
      state.loading = false
      state.data = action.payload

      state.selected = state.data.selected_configuration ?? Object.values(action.payload.schemas)[0].languageModelName
      state.settings = state.data.settings.reduce((acc, { name, value }) => ({ ...acc, [name]: value }), {})
    })

    builder.addCase(fetchLanguageModels.rejected, (state, action) => {
      state.error = action.error.message
    })
  }
})

export const { setSelectedLLMProvider, setLLMSettings } = llmProviders.actions

export default llmProviders.reducer
