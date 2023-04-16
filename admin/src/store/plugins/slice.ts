import { createAsyncThunk, createSlice } from '@reduxjs/toolkit'
import PluginModels from '@services/PluginsModels'
import { PluginsState } from './types'

const initialState: PluginsState = {
  loading: false,
  plugins: [],
  data: { plugins: [] }
}

/**
 * Async thunk that fetches the available plugins from the PluginsModels service.
 */
export const fetchPluginsModels = createAsyncThunk('plugins/fetchAll', PluginModels.getPlugins)

const pluginsSlice = createSlice({
  name: 'plugins',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder.addCase(fetchPluginsModels.pending, (state) => {
      state.loading = true
    })
    builder.addCase(fetchPluginsModels.fulfilled, (state, action) => {
      state.loading = false
      state.data = action.payload

      console.log("action", action.payload)

      state.plugins = state.data.plugins
    })
    builder.addCase(fetchPluginsModels.rejected, (state, action) => {
      state.error = action.error.message
    })
  }
})

export default pluginsSlice.reducer
