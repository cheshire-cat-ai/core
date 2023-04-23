import { createAsyncThunk, createSlice, type PayloadAction } from '@reduxjs/toolkit'
import { type LanguageModelsState } from '@store/languageModels/types'
import LanguageModelsService from '@services/LanguageModelsService'
import { toJSON } from '@utils/commons'
import { type SettingsRecord } from '@models/JSONSchemaBasedSettings'
import { type LanguageModelMetadata } from '@models/LanguageModelDescriptor'

const initialState: LanguageModelsState = {
  loading: false,
  updating: false,
  settings: {},
  data: undefined
}

/**
 * Async thunk that fetches the available language models from the LanguageModels service.
 */
export const fetchLanguageModels = createAsyncThunk('languageModels/fetchAll', LanguageModelsService.getProviders)

/**
 * Async thunk that updates the settings of a language model using the LanguageModels service.
 */
export const updateLanguageModelSettings = createAsyncThunk(
  'languageModels/updateOptions',
  (options: { name: string, settings: SettingsRecord }) => {
    const { name, settings } = options

    return LanguageModelsService.setProviderOptions(name, settings).then(toJSON)
  }
)

/**
 * The 'languageModels' slice of the redux store.
 * It contains the state of all the available language models.
 * As well as information about:
 * - the currently selected language model.
 * - the settings of each language model.
 * - the loading state of the language models when fetching them and updating them.
 */
const languageModels = createSlice({
  name: 'languageModels',
  initialState,
  reducers: {
    setSelectedLLMProvider: (state, action: PayloadAction<LanguageModelMetadata['languageModelName']>) => {
      state.selected = action.payload
    },
    setLLMSettings: (state, action: PayloadAction<{ name: string, settings: SettingsRecord }>) => {
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
      state.loading = false
      state.error = action.error.message
    })

    builder.addCase(updateLanguageModelSettings.pending, (state) => {
      state.updating = true
    })
    builder.addCase(updateLanguageModelSettings.fulfilled, (state) => {
      state.updating = false
    })
    builder.addCase(updateLanguageModelSettings.rejected, (state, action) => {
      state.updating = false
      state.error = action.error.message
    })
  }
})

export const { setSelectedLLMProvider, setLLMSettings } = languageModels.actions

export default languageModels.reducer
