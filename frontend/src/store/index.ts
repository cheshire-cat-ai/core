import { configureStore } from '@reduxjs/toolkit'
import sidebarSlice from './sidebar/slice'

const store = configureStore({
  reducer: {
    [sidebarSlice.name]: sidebarSlice.reducer
  }
})

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>

export type AppDispatch = typeof store.dispatch

export default store
