import { createSlice } from '@reduxjs/toolkit'
import { createAsyncInitialState } from '@utils/store'

const sidebarSlice = createSlice({
  name: 'faqs',
  initialState: createAsyncInitialState<string[]>([]),
  reducers: {
    fetchData: (state) => {
      state.loading = true
    }
  }
})

export const { fetchData } = sidebarSlice.actions

export default sidebarSlice
